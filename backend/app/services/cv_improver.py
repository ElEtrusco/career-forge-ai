import re


class CVImprover:

    def improve(self, text: str) -> str:
        """
        Limpieza del CV para mejorar la extracción ATS sin alterar
        el contenido original.
        """

        improved = text

        # Eliminar caracteres nulos típicos de algunos PDF
        improved = improved.replace("\x00", "")

        # Normalizar espacios
        improved = re.sub(r"[ \t]+", " ", improved)

        # Máximo dos saltos de línea consecutivos
        improved = re.sub(r"\n{3,}", "\n\n", improved)

        # Eliminar espacios al principio y final
        improved = improved.strip()

        return improved