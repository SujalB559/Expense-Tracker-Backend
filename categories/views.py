from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category
from .serializers import CategorySerializer
from .utils import seed_default_categories


class CategoryListCreateView(APIView):
    """
    GET /api/categories/
    Returns list of categories for the authenticated user.
    Supports query parameters:
      - ?type=expense or ?type=income
      - ?grouped=true: returns {'expense': [...], 'income': [...]}
    POST /api/categories/
    Creates a new custom category.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Auto-seed defaults if not already present
        if not user.categories.exists():
            seed_default_categories(user)

        queryset = user.categories.all()
        cat_type = request.query_params.get('type')
        if cat_type:
            queryset = queryset.filter(type=cat_type)

        grouped = request.query_params.get('grouped', 'false').lower() in ('true', '1')
        if grouped:
            expense_cats = queryset.filter(type='expense')
            income_cats = queryset.filter(type='income')
            return Response({
                'expense': CategorySerializer(expense_cats, many=True).data,
                'income': CategorySerializer(income_cats, many=True).data,
            })

        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH, DELETE /api/categories/<id>/
    Manages an individual category.
    Default categories can be updated (e.g., limit), but cannot be deleted.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return self.request.user.categories.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default:
            return Response(
                {'error': 'Default categories cannot be deleted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response(
            {'message': f'Category "{instance.name}" deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )
