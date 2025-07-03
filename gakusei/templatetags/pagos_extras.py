from django import template

register = template.Library()

@register.filter
def al_dia(pago, year_month):
    """
    Devuelve True si el pago tiene algún comprobante con solvencia pagada para el mes indicado (formato 'YYYY-MM').
    """
    for comprobante in pago.comprobantes.all():
        solvencia = comprobante.solvencias
        if solvencia.pagado == 'Pagado' and solvencia.mes.strftime('%Y-%m') == year_month:
            return True
    return False

@register.filter
def split(value, arg):
    """
    Divide el string por el separador dado (arg) y retorna una lista.
    """
    return value.split(arg)

@register.filter
def mes_espanol(date_obj):
    """
    Devuelve el nombre del mes en español para un objeto fecha.
    """
    meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    if hasattr(date_obj, 'month'):
        return meses[date_obj.month - 1]
    return ''

@register.filter
def mes_pagado(comprobantes, mes):
    """
    Devuelve True si existe algún comprobante pagado para el mes en español dado.
    """
    meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    for comprobante in list(comprobantes):
        solvencia = comprobante.solvencias
        if hasattr(solvencia, 'pagado') and hasattr(solvencia, 'mes'):
            if solvencia.pagado == 'Pagado' and meses[solvencia.mes.month - 1] == mes:
                return True
    return False

# Aquí puedes agregar tus filtros o tags personalizados, por ejemplo:
# @register.filter
def ejemplo(value):
    return value
