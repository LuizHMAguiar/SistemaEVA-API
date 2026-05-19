import re

def validar_cpf(cpf: str) -> bool:
    # Remove tudo que não for número
    cpf = ''.join(filter(str.isdigit, cpf))

    # Precisa ter 11 dígitos
    if len(cpf) != 11:
        return False

    # Bloqueia CPFs iguais (ex: 11111111111)
    if cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10

    # Validação final
    return cpf[-2:] == f"{dig1}{dig2}"

def validar_cnpj(cnpj: str) -> bool:
    # Remove tudo que não for número
    cnpj = ''.join(filter(str.isdigit, cnpj))

    # Precisa ter 14 dígitos
    if len(cnpj) != 14:
        return False

    # Bloqueia CNPJs com todos os dígitos iguais
    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(digito) * peso for digito, peso in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Pesos para o cálculo dos dígitos verificadores
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Primeiro dígito verificador
    dig1 = calcular_digito(cnpj[:12], pesos1)

    # Segundo dígito verificador
    dig2 = calcular_digito(cnpj[:13], pesos2)

    # Validação final
    return cnpj[-2:] == f"{dig1}{dig2}"

def validar_email(email: str) -> bool:
    # Expressão regular para validar formato de e-mail
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email:
        return False
    return bool(re.match(padrao, email))
