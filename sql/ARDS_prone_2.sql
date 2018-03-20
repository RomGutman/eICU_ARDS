-- select
--     DISTINCT
--   t.patientunitstayid as pid
--   ,t.treatmentid as tid
--   ,t.treatmentoffset as toffset
-- from
-- 	eicu_crd.treatment t
-- where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
--   and t.patientunitstayid in (select patientunitstayid from patient where patienthealthsystemstayid = 709608)
-- order by t.patientunitstayid


select
    DISTINCT
  t.patientunitstayid as pid
  ,t.treatmentid as tid
  ,t.treatmentoffset as toffset
  ,%(phsid)s as phsid
from
	eicu_crd.treatment t
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
  and t.patientunitstayid in (select patientunitstayid from patient where patienthealthsystemstayid = %(phsid)s)
order by t.patientunitstayid