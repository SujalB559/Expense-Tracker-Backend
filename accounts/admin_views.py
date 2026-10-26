from decimal import Decimal
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from accounts.models import User
from transactions.models import Transaction
from categories.models import Category


class AdminStatsView(APIView):
    """
    GET /api/admin/stats/
    High-level platform metrics for Expense Tracker Admin.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_email_verified=True).count()
        staff_users = User.objects.filter(is_staff=True).count()

        total_tx = Transaction.objects.count()
        income_sum = Transaction.objects.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        expense_sum = Transaction.objects.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return Response({
            "users": {
                "total": total_users,
                "verified": verified_users,
                "staff": staff_users,
            },
            "transactions": {
                "count": total_tx,
                "total_income": float(income_sum),
                "total_expenses": float(expense_sum),
                "volume": float(income_sum + expense_sum),
            },
            "currency": "Rs",
        })


class AdminUsersListView(APIView):
    """
    GET /api/admin/users/
    List all platform users with transaction counts and total spent.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        data = []
        for u in users:
            tx_count = u.transactions.count()
            spent = u.transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            earned = u.transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            data.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name or f"{u.first_name} {u.last_name}".strip() or u.username,
                "is_staff": u.is_staff,
                "is_superuser": u.is_superuser,
                "is_email_verified": u.is_email_verified,
                "currency": u.currency or "Rs",
                "date_joined": u.date_joined.isoformat(),
                "transactions_count": tx_count,
                "total_spent": float(spent),
                "total_earned": float(earned),
            })
        return Response(data)


class AdminUserDeleteView(APIView):
    """
    DELETE /api/admin/users/<int:pk>/
    Delete a user account.
    """
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        if request.user.id == pk:
            return Response({"error": "You cannot delete your own admin account."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target = User.objects.get(pk=pk)
            username = target.username
            target.delete()
            return Response({"message": f"User {username} deleted successfully."})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class AdminTransactionsListView(APIView):
    """
    GET /api/admin/transactions/
    Recent platform-wide transactions feed.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        txs = Transaction.objects.select_related('user', 'category').order_by('-date', '-created_at')[:100]
        data = []
        for t in txs:
            data.append({
                "id": t.id,
                "user_id": t.user.id,
                "username": t.user.username,
                "user_email": t.user.email,
                "title": t.title,
                "amount": float(t.amount),
                "type": t.type,
                "category": t.category.name if t.category else "Uncategorized",
                "category_icon": t.category.icon if t.category else "📝",
                "date": str(t.date),
                "created_at": t.created_at.isoformat() if hasattr(t, 'created_at') else None,
            })
        return Response(data)
