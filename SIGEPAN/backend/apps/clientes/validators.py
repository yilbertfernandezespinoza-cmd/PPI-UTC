import re

from django.core.exceptions import ValidationError


def validar_cedula_fisica(identificacion):
    """
    Valida una cédula física costarricense.
    Debe contener exactamente 9 dígitos.
    """

    if not re.fullmatch(r"\d{9}", identificacion):
        raise ValidationError(
            "La cédula física debe contener exactamente 9 dígitos."
        )


def validar_cedula_juridica(identificacion):
    """
    Valida una cédula jurídica.
    Debe contener exactamente 10 dígitos.
    """

    if not re.fullmatch(r"\d{10}", identificacion):
        raise ValidationError(
            "La cédula jurídica debe contener exactamente 10 dígitos."
        )


def validar_dimex(identificacion):
    """
    Valida un DIMEX.
    Debe contener entre 11 y 12 dígitos.
    """

    if not re.fullmatch(r"\d{11,12}", identificacion):
        raise ValidationError(
            "El DIMEX debe contener 11 o 12 dígitos."
        )


def validar_pasaporte(identificacion):
    """
    Valida un pasaporte.
    Permite letras y números.
    """

    if not re.fullmatch(r"[A-Za-z0-9]{6,20}", identificacion):
        raise ValidationError(
            "El pasaporte debe contener entre 6 y 20 caracteres alfanuméricos."
        )


def validar_identificacion(tipo_identificacion, identificacion):
    """
    Ejecuta la validación correspondiente según el tipo de identificación.
    """

    identificacion = identificacion.strip().upper()

    validadores = {
        "CF": validar_cedula_fisica,
        "CJ": validar_cedula_juridica,
        "DIMEX": validar_dimex,
        "PASS": validar_pasaporte,
    }

    validador = validadores.get(tipo_identificacion)

    if validador:

        validador(identificacion)

    return identificacion


def validar_telefono(telefono):
    """
    Valida un teléfono costarricense.
    """

    telefono = re.sub(r"\D", "", telefono)

    if len(telefono) != 8:

        raise ValidationError(
            "El teléfono debe contener exactamente 8 dígitos."
        )

    return telefono


def normalizar_correo(correo):
    """
    Convierte el correo a minúsculas y elimina espacios.
    """

    return correo.strip().lower()