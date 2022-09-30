SELECT ref.ReferenciaSAP, ref.Celula, eq.NombreEquipo, dep.Minifabrica, dep.CodMinif, tiempos.HorasSTD 
FROM TReferencias ref 
INNER JOIN VEquipos eq 
ON ref.CodEquipo = eq.CodEquipo
INNER JOIN VDepartamentos dep
ON eq.Departamento = dep.Departamento
INNER JOIN CReferenciasConSTD tiempos
ON ref.Referencia = tiempos.Referencia
WHERE ref.ReferenciaSAP != '' AND dep.CodMinif = 'EJYE' 
AND tiempos.Activa = 1 