"""
Entidade Sale - Camada mais pura da Clean Architecture
Contém apenas regras de negócio sem dependências externas
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import re


class PaymentStatus(Enum):
    """Status disponíveis para um pagamento"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Sale:
    """
    Entidade Sale - Representa uma venda no domínio
    
    Contém:
    - Atributos essenciais da venda
    - Regras de negócio puras (validações de CPF, etc)
    - Lógica de domínio sem dependências externas
    """
    
    def __init__(
        self,
        vehicle_id: int,
        customer_cpf: str,
        sale_date: datetime,
        amount: Decimal,
        sale_id: Optional[int] = None,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = sale_id
        self._vehicle_id = self._validate_vehicle_id(vehicle_id)
        self._customer_cpf = self._validate_cpf(customer_cpf)
        self._sale_date = self._validate_sale_date(sale_date)
        self._amount = self._validate_amount(amount)
        self._payment_status = payment_status
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
    
    # Getters (properties)
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def vehicle_id(self) -> int:
        return self._vehicle_id
    
    @property
    def customer_cpf(self) -> str:
        return self._customer_cpf
    
    @property
    def sale_date(self) -> datetime:
        return self._sale_date
    
    @property
    def amount(self) -> Decimal:
        return self._amount
    
    @property
    def payment_status(self) -> PaymentStatus:
        return self._payment_status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Métodos de negócio
    def is_payment_approved(self) -> bool:
        """Verifica se o pagamento foi aprovado"""
        return self._payment_status == PaymentStatus.APPROVED
    
    def is_payment_pending(self) -> bool:
        """Verifica se o pagamento está pendente"""
        return self._payment_status == PaymentStatus.PENDING
    
    def is_payment_rejected(self) -> bool:
        """Verifica se o pagamento foi rejeitado"""
        return self._payment_status == PaymentStatus.REJECTED
    
    def approve_payment(self) -> None:
        """Aprova o pagamento da venda"""
        if self.is_payment_approved():
            return  # Já aprovado - idempotência
        
        if self.is_payment_rejected():
            raise ValueError("Não é possível aprovar pagamento já rejeitado")
        
        self._payment_status = PaymentStatus.APPROVED
        self._updated_at = datetime.now()
    
    def reject_payment(self) -> None:
        """Rejeita o pagamento da venda"""
        if self.is_payment_rejected():
            return  # Já rejeitado - idempotência
        
        if self.is_payment_approved():
            raise ValueError("Não é possível rejeitar pagamento já aprovado")
        
        self._payment_status = PaymentStatus.REJECTED
        self._updated_at = datetime.now()
    
    def cancel_sale(self) -> None:
        """Cancela a venda (apenas se pagamento não aprovado)"""
        if self.is_payment_approved():
            raise ValueError("Não é possível cancelar venda com pagamento aprovado")
        
        self._payment_status = PaymentStatus.REJECTED
        self._updated_at = datetime.now()
    
    # Validações de negócio (regras puras)
    def _validate_vehicle_id(self, vehicle_id: int) -> int:
        """Valida o ID do veículo"""
        if not isinstance(vehicle_id, int):
            raise ValueError("ID do veículo deve ser um número inteiro")
        
        if vehicle_id <= 0:
            raise ValueError("ID do veículo deve ser maior que zero")
        
        return vehicle_id
    
    def _validate_cpf(self, cpf: str) -> str:
        """Valida o CPF do cliente - Regra de negócio pura"""
        if not cpf or not isinstance(cpf, str):
            raise ValueError("CPF é obrigatório e deve ser uma string")
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos")
        
        # Verifica se não são todos iguais
        if len(set(cpf)) == 1:
            raise ValueError("CPF não pode ter todos os dígitos iguais")
        
        # Validação do algoritmo do CPF
        if not self._validate_cpf_algorithm(cpf):
            raise ValueError("CPF inválido")
        
        # Formata o CPF
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    def _validate_cpf_algorithm(self, cpf: str) -> bool:
        """Algoritmo de validação do CPF"""
        # Primeiro dígito verificador
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        if int(cpf[9]) != digit1:
            return False
        
        # Segundo dígito verificador
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return int(cpf[10]) == digit2
    
    def _validate_sale_date(self, sale_date: datetime) -> datetime:
        """Valida a data da venda"""
        if not isinstance(sale_date, datetime):
            raise ValueError("Data da venda deve ser um datetime")
        
        # Não pode ser muito no futuro (máximo 1 dia)
        now = datetime.now()
        if sale_date > now.replace(hour=23, minute=59, second=59):
            raise ValueError("Data da venda não pode ser no futuro")
        
        # Não pode ser muito antiga (máximo 30 dias)
        days_diff = (now - sale_date).days
        if days_diff > 30:
            raise ValueError("Data da venda não pode ser anterior a 30 dias")
        
        return sale_date
    
    def _validate_amount(self, amount: Decimal) -> Decimal:
        """Valida o valor da venda"""
        if not isinstance(amount, (Decimal, int, float)):
            raise ValueError("Valor da venda deve ser um número")
        
        amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValueError("Valor da venda deve ser maior que zero")
        if amount > Decimal('9999999.99'):
            raise ValueError("Valor da venda deve ser menor que R$ 9.999.999,99")
        
        return amount.quantize(Decimal('0.01'))  # 2 casas decimais
    
    def get_cpf_numbers_only(self) -> str:
        """Retorna apenas os números do CPF"""
        return re.sub(r'[^0-9]', '', self._customer_cpf)
    
    def __str__(self) -> str:
        return f"Venda {self._id} - Veículo {self._vehicle_id} - {self._customer_cpf} - R$ {self._amount}"
    
    def __repr__(self) -> str:
        return (f"Sale(id={self._id}, vehicle_id={self._vehicle_id}, "
                f"customer_cpf='{self._customer_cpf}', amount={self._amount}, "
                f"payment_status={self._payment_status.value})")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Sale):
            return False
        return (self._vehicle_id == other._vehicle_id and 
                self._customer_cpf == other._customer_cpf and
                self._sale_date == other._sale_date)
