WITH fi as (
		SELECT
			patientunitstayid AS pid,
			labresult / 100   AS res,
			labresultoffset   AS lab_time
		FROM
			eicu_crd.lab
		WHERE
			labname = 'FiO2'
)
,pa as (
  select
      	patientunitstayid as pid
      	,labresult as res
      	,labresultoffset as lab_time
      from
      	eicu_crd.lab
      where
      	labname = 'paO2'
)


Select
  fi.pid as pid
  ,fi.res/pa.res as PF
from fi
inner join pa on pa.lab_time = fi.lab_time and pa.pid = 141227
where fi.pid = 141227