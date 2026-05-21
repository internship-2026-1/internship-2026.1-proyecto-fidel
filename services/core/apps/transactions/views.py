from django.test import TestCase
from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializers


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializers

