SELECT 'OUTGOING' as call_type, 
       calldate, src as operator, dstreal as phone, disposition as res
FROM asteriskcdr.cdr cdr
WHERE 
 date(calldate) >= dt_call_min AND date(calldate) <= dt_call_max
 AND type = 'OUTGOING'
/* AND disposition IN ('ANSWERED', 'BUSY', 'NO ANSWER') */
 and src != ''

UNION ALL 

SELECT 'INCOMING' AS call_type,
       calldate, dstchannel as operator, src as phone, disposition as res
FROM asteriskcdr.cdr
WHERE 
 date(calldate) >= dt_call_min AND date(calldate) <= dt_call_max
 AND dst = 's' and dstchannel != ''
/* and disposition IN ('ANSWERED', 'BUSY', 'NO ANSWER') */
;