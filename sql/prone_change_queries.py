patients_query = """SELECT
    DISTINCT
  t.patientunitstayid AS pid
  ,t.treatmentid AS tid
  ,t.treatmentoffset AS toffset
  ,%(phsid)s AS phsid
FROM
  eicu_crd.treatment t 
WHERE t.treatmentstring LIKE 'pulmonary|ventilation and oxygenation|prone position'
  AND t.patientunitstayid IN (SELECT patientunitstayid FROM patient WHERE patienthealthsystemstayid = %(phsid)s)
ORDER BY t.patientunitstayid"""

query = """ 
SELECT 
  fi.pid,
  fi.lab_time,
  pa.res/fi.res AS "PF ratio"
  ,%(phsid)s AS phsid
FROM 
(SELECT
      patientunitstayid AS pid
     ,CASE
        WHEN labresult IS NOT NULL THEN
          CASE
            WHEN labresult <= 1 THEN labresult
            WHEN labresult = 2 THEN 0.28
            WHEN labresult = 12 THEN 0.6
            WHEN labresult = 10 THEN 0.7
            WHEN labresult = 6 THEN 0.44
            ELSE labresult/100
          END
        WHEN labresult IS NULL AND nullif(labresulttext,'') IS NOT NULL THEN
          CASE
            WHEN replace(labresulttext,'%%','')::FLOAT = 2 THEN 0.28
            ELSE replace(labresulttext,'%%','')::FLOAT/100
          END
        ELSE NULL
      END AS res
    ,labresultoffset AS lab_time
 FROM
    eicu_crd.lab
 WHERE 
    patientunitstayid IN (SELECT patientunitstayid FROM patient
                        WHERE patienthealthsystemstayid = %(phsid)s )
    AND labname = 'FiO2') AS fi
 ,(SELECT 
    patientunitstayid AS pid
    ,CASE
      WHEN labresult IS NOT NULL THEN labresult
      WHEN labresult IS NULL AND labresulttext IS NOT NULL THEN replace(labresulttext,'<','')::NUMERIC
      ELSE NULL
    END AS res
    ,labresultoffset AS lab_time
  FROM
    eicu_crd.lab
  WHERE
    patientunitstayid IN (SELECT patientunitstayid FROM patient
                        WHERE patienthealthsystemstayid = %(phsid)s)
    AND labname = 'paO2') AS pa
WHERE pa.lab_time = fi.lab_time
AND pa.pid = fi.pid
AND fi.res IS NOT NULL
ORDER BY pa.lab_time"""


all_patiens_query = """
select DISTINCT
  p.patienthealthsystemstayid as phsid
from
  eicu_crd.treatment t
join patient as p on p.patientunitstayid = t.patientunitstayid
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
"""