-- select
-- 	distinct patientunitstayid,labname,labresult
-- from eicu_crd.lab
-- where labname = 'FiO2' or labname = 'paO2'
-- -- limit 10

select 
	fi.pid,
    fi.lab_time,
    pa.res/fi.res as "PF ratio"
from 
	(select
     	patientunitstayid as pid
     	,case
       when labresult is not NULL THEN labresult/100
       when labresult is NULL then replace(labresulttext,'%','')::FLOAT/100
      end as res
     	,labresultoffset as lab_time
     from
     	eicu_crd.lab
     where 
     	patientunitstayid in (select patientunitstayid from patient
                            where uniquepid = '006-202348')
     	and labname = 'FiO2') as fi
     ,(select 
      	patientunitstayid as pid
      	,labresult as res
      	,labresultoffset as lab_time
      from
      	eicu_crd.lab
      where
      	patientunitstayid in (select patientunitstayid from patient
                            where uniquepid = '006-202348')
      	and labname = 'paO2') as pa
where pa.lab_time = fi.lab_time
and pa.pid = fi.pid
order by pa.lab_time

-- select * from eicu_crd.diagnosis 
-- where patientunitstayid = 141168
-- 17492