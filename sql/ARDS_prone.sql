select
    DISTINCT
    apvar.patientunitstayid as pid
    ,t.treatmentid as tid
    ,t.treatmentoffset as toffset
from 
	eicu_crd.treatment t
join eicu_crd.apacheapsvar apvar on (apvar.patientunitstayid = t.patientunitstayid 
                                    and t.treatmentstring like 'pulmonary|ventilation and oxygenation|prone position'
                                    and apvar.fio2<>-1 and apvar.pao2<>-1
                                    and apvar.pao2/(apvar.fio2/100) < 200 )
order by apvar.patientunitstayid