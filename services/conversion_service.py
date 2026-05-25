class ConversionService:
    """
    Servicio de conversión inteligente de unidades para el inventario de FitGenuss.
    Soporta conversiones estándar del sistema métrico (peso y volumen)
    y conversiones personalizadas para empaques (packs, cajas a unidades).
    """

    WEIGHT_UNITS = {"mg": 0.001, "g": 1.0, "kg": 1000.0}
    VOLUME_UNITS = {"ml": 1.0, "l": 1000.0}
    COUNT_UNITS = {"unidad", "unidades", "u", "und", "base"}
    PACK_UNITS = {"pack", "packs", "paquete", "paquetes", "caja", "cajas", "compra"}

    @staticmethod
    def get_unit_family(unit: str) -> str:
        """Determina la familia física a la que pertenece una unidad dada."""
        u = unit.strip().lower()
        if u in ConversionService.WEIGHT_UNITS:
            return "PESO"
        elif u in ConversionService.VOLUME_UNITS:
            return "VOLUMEN"
        elif u in ConversionService.COUNT_UNITS or u in ConversionService.PACK_UNITS:
            return "CONTEO"
        return "OTRO"

    @staticmethod
    def convert(quantity: float, from_unit: str, to_unit: str, conversion_factor: float = 1.0) -> float:
        """
        Convierte una cantidad numérica desde una unidad de origen a una unidad de destino.
        
        Args:
            quantity: La cantidad a convertir.
            from_unit: Unidad de origen (ej. 'kg', 'pack').
            to_unit: Unidad de destino (ej. 'g', 'unidad').
            conversion_factor: Factor dinámico guardado en el ingrediente 
                               (ej. cuántos 'g' hay en 1 'kg' = 1000, o 'unidades' en 1 'pack' = 24).
        
        Returns:
            La cantidad convertida en la unidad destino.
        """
        fu = from_unit.strip().lower()
        tu = to_unit.strip().lower()

        # Si son idénticas, no requiere conversión
        if fu == tu:
            return quantity

        # 1. Conversiones de Peso
        if fu in ConversionService.WEIGHT_UNITS and tu in ConversionService.WEIGHT_UNITS:
            qty_in_g = quantity * ConversionService.WEIGHT_UNITS[fu]
            return qty_in_g / ConversionService.WEIGHT_UNITS[tu]

        # 2. Conversiones de Volumen
        if fu in ConversionService.VOLUME_UNITS and tu in ConversionService.VOLUME_UNITS:
            qty_in_ml = quantity * ConversionService.VOLUME_UNITS[fu]
            return qty_in_ml / ConversionService.VOLUME_UNITS[tu]

        # 3. Conversiones de Conteo Dinámico (Packs/Cajas a Unidades)
        # Si se convierte de empaque a unidad individual: multiplicar por factor
        if fu in ConversionService.PACK_UNITS and tu in ConversionService.COUNT_UNITS:
            return quantity * conversion_factor

        # Si se convierte de unidad individual a empaque: dividir por factor
        if fu in ConversionService.COUNT_UNITS and tu in ConversionService.PACK_UNITS:
            return quantity / conversion_factor if conversion_factor > 0 else quantity

        # 4. Caso general de fallback:
        # Si no se detectaron familias directas, pero una es de tipo 'compra' y la otra es 'base'
        # o si coincide que from_unit es la unidad de compra guardada del ingrediente
        # se asume que conversion_factor es la relación directa (Multiplicador de compra a base)
        return quantity * conversion_factor
