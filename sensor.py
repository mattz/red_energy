from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, CURRENCY
from homeassistant.helpers.entity import Entity

class RedEnergySensor(SensorEntity):
    """Representation of a Red Energy Sensor."""

    def __init__(self, name, state, attributes):
        self._name = name
        self._state = state
        self._attributes = attributes  # All the attributes from the response

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._name == "Current Consumption":
            return ENERGY_KILO_WATT_HOUR
        if self._name == "Current Charges":
            return CURRENCY
        return None

    @property
    def extra_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    async def async_update(self):
        """Fetch the latest data from the Red Energy API."""
        # The attributes are already set in the constructor, so this function can be used to refresh data if needed
        pass


def create_red_energy_sensors(data):
    """Creates Red Energy sensors from the API response data."""
    sensors = []
    
    # Extracting the relevant data from the API response
    current_usage = data.get("currentUsage", {})
    estimated_usage = data.get("estimatedUsage", {})
    billed_usage_trend = data.get("billedUsageTrend", {})
    
    # Create sensor for current consumption
    current_consumption = current_usage.get("consumptionKwh", 0.0)
    current_charges = current_usage.get("totalChargesDollar", 0.0)
    current_attributes = {
        "from_date": current_usage.get("fromDate"),
        "to_date": current_usage.get("toDate"),
        "generation_kwh": current_usage.get("generationKwh"),
        "generation_dollar": current_usage.get("generationDollar"),
        "carbon_emission_tonne": current_usage.get("carbonEmissionTonne"),
        "service_to_property_dollar": current_usage.get("serviceToPropertyDollar"),
        "gst_dollar": current_usage.get("gstDollar"),
        "demand_kw": current_usage.get("demandKw"),
        "demand_dollar": current_usage.get("demandDollar")
    }
    sensors.append(RedEnergySensor("Current Consumption", current_consumption, current_attributes))

    # Create sensor for current charges
    estimated_consumption = estimated_usage.get("consumptionKwh", 0.0)
    estimated_charges = estimated_usage.get("totalChargesDollar", 0.0)
    estimated_attributes = {
        "from_date": estimated_usage.get("fromDate"),
        "to_date": estimated_usage.get("toDate"),
        "generation_kwh": estimated_usage.get("generationKwh"),
        "generation_dollar": estimated_usage.get("generationDollar"),
        "carbon_emission_tonne": estimated_usage.get("carbonEmissionTonne"),
        "service_to_property_dollar": estimated_usage.get("serviceToPropertyDollar"),
        "gst_dollar": estimated_usage.get("gstDollar"),
        "demand_kw": estimated_usage.get("demandKw"),
        "demand_dollar": estimated_usage.get("demandDollar")
    }
    sensors.append(RedEnergySensor("Estimated Consumption", estimated_consumption, estimated_attributes))

    # Create sensor for billed usage trend
    latest_bill = billed_usage_trend.get("latestBillSummary", {})
    latest_bill_consumption = latest_bill.get("consumptionKwh", 0.0)
    latest_bill_attributes = {
        "bill_id": latest_bill.get("billId"),
        "invoice_number": latest_bill.get("invoiceNumber"),
        "from_date": latest_bill.get("fromDate"),
        "to_date": latest_bill.get("toDate"),
        "consumption_kwh": latest_bill.get("consumptionKwh")
    }
    sensors.append(RedEnergySensor("Latest Bill Consumption", latest_bill_consumption, latest_bill_attributes))

    return sensors
