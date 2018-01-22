-- SELECT
--   *
-- from diagnosis
-- where patientunitstayid = 573231

select DISTINCT patient.uniquepid
from patient
join treatment t on
                   t.treatmentstring='pulmonary|ventilation and oxygenation|prone position'
                  and t.patientunitstayid = patient.patientunitstayid



