# Categories defaults and icons matching frontend specifications

CATEGORY_ICONS = {
    'Food': '🍔',
    'Transport': '🚗',
    'Shopping': '🛍️',
    'Bills': '📄',
    'Entertainment': '🎬',
    'Health': '💊',
    'Education': '📚',
    'Salary': '💼',
    'Freelance': '💻',
    'Business': '🏢',
    'Investment': '📈',
    'Emergency Fund': '🛡️',
    'Travel': '✈️',
    'Future': '🎯',
    'Retirement': '🏖️',
    'Other': '🏷️',
}

EXPENSE_DEFAULTS = [
    'Food',
    'Transport',
    'Shopping',
    'Bills',
    'Entertainment',
    'Health',
    'Education',
    'Other',
]

INCOME_DEFAULTS = [
    'Salary',
    'Freelance',
    'Business',
    'Investment',
    'Other',
]

SAVINGS_DEFAULTS = [
    'Emergency Fund',
    'Travel',
    'Future',
    'Investment',
    'Other',
]


def seed_default_categories(user):
    """
    Populate default expense, income, and savings categories for a user if not already present.
    """
    from .models import Category

    for name in EXPENSE_DEFAULTS:
        Category.objects.get_or_create(
            user=user,
            name=name,
            type='expense',
            defaults={
                'icon': CATEGORY_ICONS.get(name, '🏷️'),
                'is_default': True,
            },
        )

    for name in INCOME_DEFAULTS:
        Category.objects.get_or_create(
            user=user,
            name=name,
            type='income',
            defaults={
                'icon': CATEGORY_ICONS.get(name, '🏷️'),
                'is_default': True,
            },
        )

    for name in SAVINGS_DEFAULTS:
        Category.objects.get_or_create(
            user=user,
            name=name,
            type='savings',
            defaults={
                'icon': CATEGORY_ICONS.get(name, '🏷️'),
                'is_default': True,
            },
        )
