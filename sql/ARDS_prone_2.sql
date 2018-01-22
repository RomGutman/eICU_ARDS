select
    DISTINCT
    t.patientunitstayid as pid
    ,t.treatmentid as tid
    ,t.treatmentoffset as toffset
from
	eicu_crd.treatment t
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
  and t.patientunitstayid = 978712
order by t.patientunitstayid