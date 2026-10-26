from datetime import datetime, date
from django.core.management.base import BaseCommand
from accounts.models import User
from categories.utils import seed_default_categories
from transactions.models import Transaction
from budgets.models import MonthlyBudget, SavingsGoal


class Command(BaseCommand):
    help = 'Seeds initial demo user and transactions matching frontend starter data'

    def handle(self, *args, **options):
        # Create or update demo user
        user, created = User.objects.get_or_create(
            username='jordan',
            defaults={
                'email': 'jordan@example.com',
                'first_name': 'Jordan',
                'last_name': 'Davis',
                'currency': '$',
                'theme': 'light',
            },
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user: jordan (password: password123)'))
        else:
            self.stdout.write('Demo user "jordan" already exists.')

        # Seed categories
        seed_default_categories(user)

        # Set category limits (e.g., Food: 400, Transport: 150)
        user.categories.filter(name='Food', type='expense').update(limit=400.00)
        user.categories.filter(name='Transport', type='expense').update(limit=150.00)

        # Seed Monthly Budget
        MonthlyBudget.objects.get_or_create(
            user=user,
            defaults={'amount': 2000.00},
        )

        # Seed Savings Goals
        SavingsGoal.objects.get_or_create(
            user=user,
            name='Emergency Fund',
            defaults={'target': 5000.00, 'saved': 1500.00},
        )
        SavingsGoal.objects.get_or_create(
            user=user,
            name='Vacation Trip',
            defaults={'target': 2000.00, 'saved': 800.00},
        )

        # Seed starter transactions (using current month/dates)
        today = date.today()
        current_year = today.year
        current_month = today.month

        demo_transactions = [
            {
                'name': 'Monthly salary',
                'amount': 4800.00,
                'type': 'income',
                'category': 'Salary',
                'date': date(current_year, current_month, 1),
                'description': 'Monthly salary payment',
                'icon': '💼',
                'recurring': True,
                'repeat': 'monthly',
            },
            {
                'name': 'Whole Foods Market',
                'amount': 86.40,
                'type': 'expense',
                'category': 'Food',
                'date': date(current_year, current_month, min(today.day, 8)),
                'description': 'Weekly groceries',
                'icon': '🍔',
                'recurring': False,
                'repeat': 'monthly',
            },
            {
                'name': 'Adobe Creative Cloud',
                'amount': 54.99,
                'type': 'expense',
                'category': 'Bills',
                'date': date(current_year, current_month, min(today.day, 6)),
                'description': 'Monthly subscription',
                'icon': '📄',
                'recurring': True,
                'repeat': 'monthly',
            },
            {
                'name': 'Freelance project',
                'amount': 950.00,
                'type': 'income',
                'category': 'Freelance',
                'date': date(current_year, current_month, min(today.day, 4)),
                'description': 'Brand identity project',
                'icon': '💻',
                'recurring': False,
                'repeat': 'monthly',
            },
            {
                'name': 'City transit pass',
                'amount': 72.00,
                'type': 'expense',
                'category': 'Transport',
                'date': date(current_year, current_month, min(today.day, 3)),
                'description': 'Monthly metro pass',
                'icon': '🚗',
                'recurring': True,
                'repeat': 'monthly',
            },
        ]

        # Only add transactions if user has none
        if not user.transactions.exists():
            for t in demo_transactions:
                Transaction.objects.create(user=user, **t)
            self.stdout.write(self.style.SUCCESS(f'Created {len(demo_transactions)} demo transactions.'))
        else:
            self.stdout.write('User already has transactions; skipping demo transactions.')

        self.stdout.write(self.style.SUCCESS('Demo data seed completed successfully.'))
