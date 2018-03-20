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
       when labresult is not NULL THEN
			   case
			     when labresult <= 1 then labresult
		       when labresult = 2 then 0.28
					 when labresult = 12 then 0.6
					 when labresult = 10 then 0.7
					 when labresult = 6 then 0.44
				   else labresult/100
				  end
       when labresult is NULL and nullif(labresulttext,'') is NOT NULL then
				 case
					 when replace(labresulttext,'%','')::FLOAT = 2 then 0.28
				   else replace(labresulttext,'%','')::FLOAT/100
				 end
			 else NULL
      end as res
     	,labresultoffset as lab_time
     from
     	eicu_crd.lab
     where 
     	patientunitstayid in (select patientunitstayid from patient
                            where patienthealthsystemstayid = 571715)
     	and labname = 'FiO2') as fi
     ,(select 
      	patientunitstayid as pid
      	,case
           when labresult is not null then labresult
           when labresult is null and labresulttext is not null then replace(labresulttext,'<','')::NUMERIC
           else NULL
         end as res
      	,labresultoffset as lab_time
      from
      	eicu_crd.lab
      where
      	patientunitstayid in (select patientunitstayid from patient
                            where patienthealthsystemstayid = 571715)
      	and labname = 'paO2') as pa
where pa.lab_time = fi.lab_time
and pa.pid = fi.pid
and fi.res is not NULL
order by pa.lab_time

-- select * from eicu_crd.diagnosis 
-- where patientunitstayid = 141168
-- 17492

--709608
