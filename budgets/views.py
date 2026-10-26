from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MonthlyBudget, SavingsGoal
from .serializers import MonthlyBudgetSerializer, SavingsGoalSerializer


class MonthlyBudgetView(APIView):
    """
    GET /api/budgets/
    Returns user's monthly budget info and current monthly progress.

    PUT /api/budgets/
    PATCH /api/budgets/
    Updates user's monthly budget limit amount.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = MonthlyBudget.objects.get_or_create(
            user=self.request.user,
            defaults={'amount': 2000.00},
        )
        return obj

    def get(self, request):
        budget = self.get_object()
        serializer = MonthlyBudgetSerializer(budget)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        budget = self.get_object()
        serializer = MonthlyBudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class SavingsGoalListCreateView(APIView):
    """
    GET /api/budgets/goals/
    Lists all savings goals for the authenticated user.

    POST /api/budgets/goals/
    Creates a new savings goal.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = request.user.savings_goals.all()
        serializer = SavingsGoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SavingsGoalSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavingsGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH, DELETE /api/budgets/goals/<id>/
    Manages an individual savings goal.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SavingsGoalSerializer

    def get_queryset(self):
        return self.request.user.savings_goals.all()
