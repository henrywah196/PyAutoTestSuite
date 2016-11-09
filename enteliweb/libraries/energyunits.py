'''
Created on Oct 6, 2016

@author: hwang
'''
from pint import UnitRegistry

class EnergyUnits:
    
    def __init__(self):
        self.ureg = UnitRegistry()
        
        self.ureg.define('kilo_watt_hour = 1000 * watt_hour = KWh')
        self.ureg.define('mega_watt_hour = 1000 * kilo_watt_hour = MWh')
        self.ureg.define('giga_watt_hour = 1000 * mega_watt_hour = GWh')
        
        self.ureg.define('megajoule_per_hour = 277.777777778 * watt')
        self.ureg.define('megajoule_per_second = 3600.0 * megajoule_per_hour')
        self.ureg.define('kilo_watt = 1000 * watt = KW')
        self.ureg.define('mega_watt = 1000 * kilo_watt = MW')
        
        self.ureg.define('KVAh = 1.0')
        self.ureg.define('MVAh = 1000 * KVAh')
        self.ureg.define('GVAh = 1000 * MVAh')
        
        self.ureg.define('KVA = 1.0')
        self.ureg.define('MVA = 1000 * KVA')
        
        self.ureg.define('cubic_meter = 35.3147 * cubic_foot')
        self.ureg.define('CCF = 100 * cubic_foot')
        
        self.ureg.define('cubic_foot_per_minute = 1.0')
        self.ureg.define('cubic_foot_per_hour = 0.0166666666666667 * cubic_foot_per_minute')
        self.ureg.define('cubic_meter_per_hour = 35.3147 * cubic_foot_per_hour')
        
        self.ureg.define('kbtu = 1000 * btu')
        self.ureg.define('ton_h = 12000 * btu')
        
        self.ureg.define('btu_per_hour = 0.293071070172 * watt')
        self.ureg.define('gigajoule_per_hour = 1000 * megajoule_per_hour')
        self.ureg.define('thm_per_hour = 29307.1070172 * watt')
        self.ureg.define('Tons = 12000 * btu_per_hour')
        
        self.ureg.define('liter_per_hour = 0.001 * cubic_meter_per_hour')
        self.ureg.define('liter_per_minute = 60.0 * liter_per_hour')
        self.ureg.define('liter_per_second = 60.0 * liter_per_minute')
        self.ureg.define('imp_gph = 4.54609 * liter_per_hour')
        self.ureg.define('imp_gpm = 4.54609 * liter_per_minute')
        self.ureg.define('US_gph = 3.785411784 * liter_per_hour')
        self.ureg.define('US_gpm = 3.785411784 * liter_per_minute')
        
        self.ureg.define('RT = 12000.0 * btu_per_hour')
        
        self.ureg.define('pound_per_hour = 1.0')
        self.ureg.define('kilogram_per_hour = 2.20462262185 * pound_per_hour')
        
        # mapping eweb energy units symbol to Pint units
        self.mapping = {
                          "WATTHOUR"       : "Wh",
                          "KILOWATT_HOUR"  : "KWh",
                          "MEGAWATTHOUR"   : "MWh",
                          "GIGAWATT_HOUR"  : "GWh",
                          "MEGAJOULE"      : "MJ",
                          
                          "WATT"               : "W",
                          "KILOWATT"           : "KW",
                          "MEGAWATT"           : "MW",
                          "MEGAJOULE_PER_HOUR" : "megajoule_per_hour",
                          
                          "KILOVOLTAMP_HOUR"   : "KVAh",
                          "MEGAVOLTAMP_HOUR"   : "MVAh",
                          "GIGAVOLTAMP_HOUR"   : "GVAh",
                          
                          "KILOVOLTAMP"  : "KVA",
                          "MEGAVOLTAMP"  : "MVA",
                          
                          "CUBIC_METER"         : "cubic_meter",
                          "CUBIC_FOOT"          : "cubic_foot",
                          "HUNDRED_CUBIC_FEET"  : "CCF",
                          
                          "CUBIC_FOOT_PER_HOUR"   : "cubic_foot_per_hour",
                          "CUBIC_FOOT_PER_MINUTE" : "cubic_foot_per_minute",
                          "CUBIC_METER_PER_HOUR"  : "cubic_meter_per_hour",
                          
                          "BTU"                        : "btu",
                          "THOUSAND_BTU"               : "kbtu",
                          "TON_OF_REFRIGERATION_HOURS" : "ton_h",
                          "GIGAJOULE"                  : "GJ",
                          "THERM"                      : "thm",
                          
                          "BTU_PER_HOUR"              : "btu_per_hour",
                          "TON_OF_REFRIGERATION_TON"  : "Tons",
                          "GIGAJOULE_PER_HOUR"        : "gigajoule_per_hour",
                          "THERM_PER_HOUR"            : "thm_per_hour",
                          
                          "LITER"      : "liter",
                          "GALLON"     : "imperial_gallon",
                          "GALLON_US"  : "gallon",
                          
                          "GALLON_PER_HOUR"      : "imp_gph",
                          "GALLON_PER_MINUTE"    : "imp_gpm",
                          "GALLON_US_PER_HOUR"   : "US_gph",
                          "GALLON_US_PER_MINUTE" : "US_gpm",
                          "LITER_PER_HOUR"       : "liter_per_hour",
                          "LITER_PER_MINUTE"     : "liter_per_minute",
                          "LITER_PER_SECOND"     : "liter_per_second",
                          
                          "MEGAJOULE_PER_SECOND"    : "megajoule_per_second",
                          "TON_OF_REFRIGERATION"    : "RT",
                          
                          "KILOGRAM"      : "kilogram",
                          "POUND"         : "lb",
                          
                          "KILOGRAM_PER_HOUR" : "kilogram_per_hour",
                          "POUND_PER_HOUR"    : "pound_per_hour",
                          
                          "TON"       : "tonne",
                          "TON_US"    : "ton",
                          
                          "CELSIUS"    : "degC",
                          "FAHRENHEIT" : "degF"
                          
                       }
        
        
        self.energyTypes = {
                             "Energy_Electric"          : [],
                             "Power_Electric"           : [],
                             "Apparent_Energy_Electric" : [],
                             "Apparent_Power_Electric"  : [],
                             "Volume_Gas"               : [],
                             "Flow_Volume_Gas"          : [],
                             "Energy_Gas"               : [],
                             "Power_Gas"                : [],
                             "Volume_Fuel"              : [],
                             "Flow_Volume_Fuel"         : [],
                             "Volume_Water"             : [],
                             "Flow_Volume_Water"        : [],
                             "Energy_Thermal"           : [],
                             "Power_Thermal"            : [],
                             "Weight_Steam"             : [],
                             "Flow_Mass_Steam"          : [],
                             "Weight_Carbon"            : [],
                             "Temperature"              : ["CELSIUS", "FAHRENHEIT"]
                           }
        
        
    def convert(self, unitFrom, unitTo, value):
        """
        convert the value from the "From" unit to "to" unit
        """
        if unitFrom in ["CELSIUS", "FAHRENHEIT"]:
            return self._degConvert(unitFrom, unitTo, value)
        else:
            pintUnitFrom = self.mapping["unitFrom"]
            pintUnitTo = self.mapping["unitTo"]
        
            fm = 1 * self.ureg.parse_units(pintUnitFrom)
            to = fm.to(pintUnitTo)
        
            return to.magnitude * float(value)
    
    
    def _degConvert(self, unitFrom, unitto, value):
        
        pintUnitFrom = self.mapping["unitFrom"]
        pintUnitTo = self.mapping["unitTo"]
        Q_ = self.ureg.Quantity
        fm = Q_(value, self.ureg.parse_units(pintUnitFrom))
        to = fm.to(pintUnitTo)
        return to.magnitude
        
        
        
if __name__ == "__main__":

    myUnit = EnergyUnits()
    ureg = myUnit.ureg
    
    print "# Electric"
    fm = 1 * ureg.MJ
    print "%s equals to: "%fm
    print fm.to("Wh")
    print fm.to("KWh")
    print fm.to("MWh")
    print fm.to("GWh")
    
    fm = 1 * ureg.KW
    print "\n%s equals to: "%fm
    print fm.to("W")
    print fm.to("MW")
    print fm.to("megajoule_per_hour")
    
    fm = 1 * ureg.KVAh
    print "\n%s equals to: "%fm
    print fm.to("MVAh")
    print fm.to("GVAh")
    
    fm = 1 * ureg.KVA
    print "\n%s equals to: "%fm
    print fm.to("MVA")
    
    print "# Gas"
    fm = 1 * ureg.cubic_meter
    print "\n%s equals to: "%fm
    print fm.to("cubic_foot")
    print fm.to("CCF")
    
    fm = 1 * ureg.cubic_foot_per_hour
    print "\n%s equals to: "%fm
    print fm.to("cubic_meter_per_hour")
    print fm.to("cubic_foot_per_minute")
    
    fm = 1 * ureg.btu
    print "\n%s equals to: "%fm
    print fm.to("kbtu")
    print fm.to("ton_h")
    print fm.to("MJ")
    print fm.to("GJ")
    print fm.to("thm")
    print fm.to("KWh")
    
    fm = 1 * ureg.btu_per_hour
    print "\n%s equals to: "%fm
    print fm.to("Tons")
    print fm.to("megajoule_per_hour")
    print fm.to("gigajoule_per_hour")
    print fm.to("thm_per_hour")
    print fm.to("KW")
    
    print "# fuel"
    fm = 1 * ureg.liter
    print "\n%s equals to: "%fm
    print fm.to("imperial_gallon")
    print fm.to("gallon")
    
    fm = 1 * ureg.imp_gph
    print "\n%s equals to: "%fm
    print fm.to("imp_gpm")
    print fm.to("US_gph")
    print fm.to("US_gpm")
    print fm.to("liter_per_hour")
    print fm.to("liter_per_minute")
    print fm.to("liter_per_second")
    
    print"# water"
    fm = 1 * ureg.cubic_meter
    print "\n%s equals to: "%fm
    print fm.to("cubic_foot")
    print fm.to("imperial_gallon")
    print fm.to("gallon")
    print fm.to("liter")
    
    fm = 1 * ureg.cubic_meter_per_hour
    print "\n%s equals to: "%fm
    print fm.to("cubic_foot_per_hour")
    print fm.to("cubic_foot_per_minute")
    print fm.to("imp_gph")
    print fm.to("imp_gpm")
    print fm.to("US_gph")
    print fm.to("US_gpm")
    print fm.to("liter_per_hour")
    print fm.to("liter_per_minute")
    print fm.to("liter_per_second")
    
    print "# Thermal"
    fm = 1 * ureg.KWh
    print "\n%s equals to: "%fm
    print fm.to("MWh")
    print fm.to("btu")
    print fm.to("kbtu")
    print fm.to("ton_h")
    print fm.to("MJ")
    print fm.to("GJ")
    
    fm = 1 * ureg.KW
    print "\n%s equals to: "%fm
    print fm.to("MW")
    print fm.to("btu_per_hour")
    print fm.to("megajoule_per_hour")
    print fm.to("megajoule_per_second")
    print fm.to("gigajoule_per_hour")
    print fm.to("RT")
    
    
    
    
    
    
    
    
    
    
    
    
        
    