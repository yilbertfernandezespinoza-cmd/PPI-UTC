from django.conf import settings
from django.core.exceptions import ValidationError

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _obtener_credenciales(usuario):
    """
    Construye las credenciales de Google a partir del token guardado
    en el usuario, renovándolas si ya vencieron.
    """

    if not usuario.google_token:
        raise ValidationError(
            "Debes vincular tu cuenta de Google antes de exportar a Sheets."
        )

    credenciales = Credentials(
        token=usuario.google_token,
        refresh_token=usuario.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

    if not credenciales.valid:

        if credenciales.expired and credenciales.refresh_token:

            try:
                credenciales.refresh(Request())

            except Exception:
                raise ValidationError(
                    "Tu sesión de Google venció. Vuelve a vincular tu cuenta desde tu perfil."
                )

            # Guardamos el token renovado para no repetir el refresh innecesariamente
            usuario.google_token = credenciales.token
            usuario.save(update_fields=["google_token"])

        else:
            raise ValidationError(
                "Tu sesión de Google venció. Vuelve a vincular tu cuenta desde tu perfil."
            )

    return credenciales


def exportar_a_google_sheets(usuario, titulo, encabezados, filas):
    """
    Crea una hoja de cálculo nueva en la cuenta de Google del usuario
    con los datos del reporte, y devuelve la URL para abrirla.
    """

    credenciales = _obtener_credenciales(usuario)

    servicio = build("sheets", "v4", credentials=credenciales)

    try:

        hoja = servicio.spreadsheets().create(
            body={"properties": {"title": titulo}}
        ).execute()

        spreadsheet_id = hoja["spreadsheetId"]

        valores = [encabezados] + [
            [str(celda) for celda in fila]
            for fila in filas
        ]

        servicio.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range="A1",
            valueInputOption="RAW",
            body={"values": valores},
        ).execute()

        return hoja["spreadsheetUrl"]

    except HttpError as error:
        raise ValidationError(
            f"No se pudo crear la hoja de cálculo en Google Sheets: {error}"
        )