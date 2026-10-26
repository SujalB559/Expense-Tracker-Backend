from datetime import datetime, date
from decimal import Decimal
from django.db.models import Q, Sum
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListCreateView(APIView):
    """
    GET /api/transactions/
    Lists transactions with filtering and search support.
    Query parameters supported:
      - search: string to search in name, category, or description
      - type: 'all' | 'income' | 'expense'
      - category: 'all' | category name
      - sort: 'date' (newest first) | 'amount' (highest first)
      - month: YYYY-MM (e.g. '2024-06')
      - limit: integer to limit results (e.g. limit=5 for recent transactions)

    POST /api/transactions/
    Creates a new transaction for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = user.transactions.all()

        # Search filter
        search = request.query_params.get('search')
        if search:
            search = search.strip()
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(category__icontains=search) |
                Q(description__icontains=search)
            )

        # Type filter
        trans_type = request.query_params.get('type')
        if trans_type and trans_type != 'all':
            queryset = queryset.filter(type=trans_type)

        # Category filter
        category = request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category__iexact=category)

        # Month filter (YYYY-MM)
        month = request.query_params.get('month')
        if month:
            try:
                year_part, month_part = month.split('-')
                queryset = queryset.filter(date__year=int(year_part), date__month=int(month_part))
            except ValueError:
                pass

        # Sorting
        sort_by = request.query_params.get('sort', 'date')
        if sort_by == 'amount':
            queryset = queryset.order_by('-amount', '-date')
        else:
            queryset = queryset.order_by('-date', '-id')

        # Limit
        limit = request.query_params.get('limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH, DELETE /api/transactions/<id>/
    Retrieves, updates, or deletes an existing transaction.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return self.request.user.transactions.all()


class TransactionSummaryView(APIView):
    """
    GET /api/transactions/summary/
    Returns aggregate financial statistics and monthly activity for Dashboard and Analytics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = user.transactions.all()

        total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_expenses = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_savings = transactions.filter(type='savings').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        balance = total_income - total_expenses - total_savings

        savings_rate = 0
        if total_income > 0:
            savings_rate = round(float((total_income - total_expenses) / total_income) * 100)

        # Current month activity
        now = datetime.now()
        current_month_key = now.strftime('%Y-%m')
        month_expenses_qs = transactions.filter(
            type='expense',
            date__year=now.year,
            date__month=now.month,
        )
        month_expenses = month_expenses_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        month_savings_qs = transactions.filter(
            type='savings',
            date__year=now.year,
            date__month=now.month,
        )
        month_savings = month_savings_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Category totals for current month
        category_totals = {}
        for item in month_expenses_qs:
            cat = item.category
            category_totals[cat] = category_totals.get(cat, 0.0) + float(item.amount)

        # Top expense category this month
        top_category = None
        if category_totals:
            top_category_name = max(category_totals, key=category_totals.get)
            top_category = [top_category_name, category_totals[top_category_name]]

        # Last 6 months activity for charts
        monthly_activity = []
        for i in range(5, -1, -1):
            # Calculate year and month for 6 months ago to current
            month_calc = now.month - i
            year_calc = now.year
            while month_calc <= 0:
                month_calc += 12
                year_calc -= 1

            month_date = date(year_calc, month_calc, 1)
            month_label = month_date.strftime('%b')
            key = month_date.strftime('%Y-%m')

            inc = transactions.filter(
                type='income',
                date__year=year_calc,
                date__month=month_calc,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            exp = transactions.filter(
                type='expense',
                date__year=year_calc,
                date__month=month_calc,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            sav = transactions.filter(
                type='savings',
                date__year=year_calc,
                date__month=month_calc,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            monthly_activity.append({
                'month': month_label,
                'key': key,
                'income': float(inc),
                'expense': float(exp),
                'savings': float(sav),
            })

        return Response({
            'balance': float(balance),
            'income': float(total_income),
            'expenses': float(total_expenses),
            'savings': float(total_savings),
            'savingsRate': savings_rate,
            'monthExpenses': float(month_expenses),
            'monthSavings': float(month_savings),
            'topCategory': top_category,
            'categoryTotals': category_totals,
            'monthlyActivity': monthly_activity,
        }, status=status.HTTP_200_OK)


class ClearTransactionsView(APIView):
    """
    POST /api/transactions/clear/
    Clears all transactions belonging to the current user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count, _ = request.user.transactions.all().delete()
        return Response(
            {'message': f'Successfully cleared {count} transactions.'},
            status=status.HTTP_200_OK,
        )
