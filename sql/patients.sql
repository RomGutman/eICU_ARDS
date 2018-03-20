select count(DISTINCT patienthealthsystemstayid)
from patient

-- select wardid, count(DISTINCT unittype) as counts
--   from patient
-- GROUP BY wardid
-- ORDER BY counts desc
--
--
-- select count(DISTINCT uniquepid)
-- from patient 1100383

select
  DISTINCT
--   t.patientunitstayid as pid
--   ,p.uniquepid as upid
  p.patienthealthsystemstayid as phsid
  ,p.age as age
from
	eicu_crd.treatment t
join patient as p on p.patientunitstayid = t.patientunitstayid
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position';
-- order by t.patientunitstayid


select * from patient
where patienthealthsystemstayid = 2637281


select * from diagnosis
where patientunitstayid = 494141

-- good example: 814543,824513,2621881,2645908
-- to check later : 1109600,1109601
select * from lab
where patientunitstayid=624235 and labtypeid = 7 and (labname = 'FiO2' or labname = 'paO2') and labmeasurenameinterface = 'lpm'
order by labresultoffset, labresultrevisedoffset

-- select DISTINCT labname from lab
-- where labtypeid = 7


with p_list as(
select DISTINCT
  p.patienthealthsystemstayid as phsid
from
  eicu_crd.treatment t
join patient as p on p.patientunitstayid = t.patientunitstayid
-- LEFT OUTER JOIN diagnosis as d on d.patientunitstayid = p.patientunitstayid and
--                                   (d.icd9code like '%518.82%' or d.icd9code like '%J80%' or d.icd9code like '%518.5%')
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
-- and d.patientunitstayid is NULL
GROUP BY phsid)

select DISTINCT
  p.patienthealthsystemstayid as phsid
--   ,d.diagnosisstring
--   ,d.icd9code
--   ,string_agg(DISTINCT p.unitdischargestatus,',')
from patient as p
join p_list on p_list.phsid = p.patienthealthsystemstayid
-- join diagnosis as d on p.patientunitstayid = d.patientunitstayid and d.diagnosisstring like '%pulmonary%'
-- GROUP BY  patienthealthsystemstayid




-- order by t.patientunitstayid)
-- order by observationoffset desc


select DISTINCT treatmentstring from treatment
where treatmentstring like '%position%'

select
  DISTINCT
--   t.patientunitstayid as pid
--   ,p.uniquepid as upid
  p.patienthealthsystemstayid as phsid
  ,p.age as age
  ,p.unitdischargestatus
  ,p.apacheadmissiondx
  ,p.unitdischargestatus
from
	eicu_crd.treatment t
join patient as p on p.patientunitstayid = t.patientunitstayid
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position';
-- order by t.patientunitstayid

select
  patientunitstayid,
  vp.observationoffset
  ,respiration
  ,heartrate
  ,sao2
from vitalperiodic vp
where patientunitstayid in (select patientunitstayid from patient
                            where patienthealthsystemstayid = 814543 )
order by observationoffset






select DISTINCT
  p.patienthealthsystemstayid as phsid
  ,p.age as age
  ,p.gender
  ,p.ethnicity
from
  patient as p
INNER JOIN diagnosis as d on d.patientunitstayid = p.patientunitstayid and
                                  (d.icd9code like '%518.82%' or d.icd9code like '%J80%' or d.icd9code like '%518.5%')


with p_list as(
select DISTINCT
  p.patienthealthsystemstayid as phsid
from
  eicu_crd.treatment t
join patient as p on p.patientunitstayid = t.patientunitstayid
-- LEFT OUTER JOIN diagnosis as d on d.patientunitstayid = p.patientunitstayid and
--                                   (d.icd9code like '%518.82%' or d.icd9code like '%J80%' or d.icd9code like '%518.5%')
where t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
-- and d.patientunitstayid is NULL
GROUP BY phsid)


select DISTINCT
  p.patientunitstayid as pid
  ,p.patienthealthsystemstayid as phsid
  ,l.labid
  ,l.labresult
  ,l.labresulttext
  ,l.labmeasurenamesystem
  ,l.labmeasurenameinterface
  ,l.labresultoffset
  ,p.hospitalid
from
  patient p
join p_list on p_list.phsid = p.patienthealthsystemstayid
join (select * from lab where labtypeid = 7 and (labname = 'FiO2' )
                              and (
                                (
                                  (labresult is NULL and nullif(labresulttext,'') is NOT NULL)
                                  and
                                  (replace(labresulttext,'%','')::FLOAT < 21)
                                )
                                 or
                                (
                                  (labresult is not NULL )
                                  AND
                                  (labresult < 21)
                                )
                              )
     )
    as l on l.patientunitstayid = p.patientunitstayid

-- select DISTINCT
--   p.patientunitstayid as pid
--   ,p.patienthealthsystemstayid as phsid
--   ,l.labid
-- from
--   patient p
-- join p_list on p_list.phsid = p.patienthealthsystemstayid
-- join (select * from lab where labtypeid = 7 and (labname = 'FiO2' or labname = 'paO2') and labmeasurenameinterface = 'lpm')
--     as l on l.patientunitstayid = p.patientunitstayid
-- and d.patientunitstayid is NULL
-- GROUP BY phsid



select * from lab
where labid in (224974833,220935778,221237578,221654410,224395578,225909817,225918948,225928241,226312187,226397604,226926615,220654492,222780030,225869349,225979356)

select DISTINCT
labmeasurenamesystem
from lab
where labname = 'FiO2'

select * from vitalaperiodic
where patientunitstayid = 624235


select * from treatment
where patientunitstayid = 3214853
and treatmentstring like 'pulmonary%' --|ventilation and oxygenation%'

select * from treatment t
where patientunitstayid in (
  select patient.patientunitstayid
  from patient
where uniquepid = '033-25690'
)
  and t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
order by treatmentoffset


select *
  from patient
where patienthealthsystemstayid = 2644190
--where uniquepid = '033-25690' --patientunitstayid = 3215590


select * from lab
where patientunitstayid = 735589
and labtypeid = 7
order by labresultoffset
-- in (
--   select patient.patientunitstayid
--   from patient
-- where uniquepid = '033-25690'
-- )