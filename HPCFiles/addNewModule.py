import bifacial_radiance

rad_obj = bifacial_radiance.RadianceObj('makemod', 'TEMP')

rad_obj.getEPW(37.42, -110)

moduletype='PVmodule'
x = 1
y = 2
rad_obj.makeModule(name=moduletype, x=x, y=y)

moduletype='PVmodule2up'
rad_obj.makeModule(name=moduletype, x=x, y=y, numpanels=2)


moduletype='PVmodule_1mxgap'
rad_obj.makeModule(name=moduletype, x=x, y=y, xgap = 1.0)

moduletype='PVmodule2up_1mxgap'
rad_obj.makeModule(name=moduletype, x=x, y=y, numpanels=2, xgap = 1.0)

