* Dump schema, index tags, and RI rules of a DBC and some free tables to JSON-ish text.
LPARAMETERS tcDbc, tcOut, tcFree
LOCAL lnH, i, j, n, lcT, lcLine, laF[1], laT[1], lcRel, laFree[1], nFree
PRIVATE gnDumpH
ON ERROR DO dumperr WITH MESSAGE(), LINENO()
SET EXCLUSIVE OFF
SET SAFETY OFF
lnH = FCREATE(tcOut)
gnDumpH = lnH
OPEN DATABASE (tcDbc) SHARED
SET DATABASE TO (JUSTSTEM(tcDbc))
n = ADBOBJECTS(laT, "TABLE")
FOR i = 1 TO n
  lcT = laT[i]
  USE (lcT) IN 0 SHARED ALIAS dumptbl
  SELECT dumptbl
  FPUTS(lnH, "TABLE|" + lcT + "|" + DBF() + "|" + TRANSFORM(RECCOUNT()) + "|" + DBGETPROP(lcT,"TABLE","Comment") + "|" + DBGETPROP(lcT,"TABLE","RuleExpression") + "|" + DBGETPROP(lcT,"TABLE","RuleText") + "|" + DBGETPROP(lcT,"TABLE","InsertTrigger") + "|" + DBGETPROP(lcT,"TABLE","UpdateTrigger") + "|" + DBGETPROP(lcT,"TABLE","DeleteTrigger") + "|" + DBGETPROP(lcT,"TABLE","PrimaryKey"))
  AFIELDS(laF, "dumptbl")
  FOR j = 1 TO ALEN(laF,1)
    lcLine = "FIELD|" + laF[j,1] + "|" + laF[j,2] + "|" + TRANSFORM(laF[j,3]) + "|" + TRANSFORM(laF[j,4]) + "|" + IIF(laF[j,5],"Y","N") + "|" + laF[j,7] + "|" + laF[j,8] + "|" + laF[j,9] + "|" + STRTRAN(STRTRAN(DBGETPROP(lcT+"."+laF[j,1],"FIELD","Comment"),CHR(13)," "),CHR(10)," ") + "|" + DBGETPROP(lcT+"."+laF[j,1],"FIELD","Caption") + "|" + DBGETPROP(lcT+"."+laF[j,1],"FIELD","InputMask") + "|" + DBGETPROP(lcT+"."+laF[j,1],"FIELD","Format")
    FPUTS(lnH, lcLine)
  ENDFOR
  FOR j = 1 TO TAGCOUNT()
    IF EMPTY(TAG(j))
      LOOP
    ENDIF
    lcLine = "TAG|" + TAG(j) + "|" + KEY(j) + "|" + FOR(j) + "|" + IIF(PRIMARY(j),"PRIMARY",IIF(CANDIDATE(j),"CANDIDATE",IIF(UNIQUE(j),"UNIQUE","REGULAR"))) + "|" + IIF(DESCENDING(j),"DESC","ASC")
    FPUTS(lnH, lcLine)
  ENDFOR
  USE IN dumptbl
  FFLUSH(lnH)
ENDFOR
n = ADBOBJECTS(laT, "CONNECTION")
n = ADBOBJECTS(laT, "VIEW")
FOR i = 1 TO n
  FPUTS(lnH, "VIEW|" + laT[i] + "|" + STRTRAN(STRTRAN(DBGETPROP(laT[i],"VIEW","SQL"),CHR(13)," "),CHR(10)," ") + "|" + IIF(DBGETPROP(laT[i],"VIEW","SendUpdates"),"updatable","readonly") + "|" + DBGETPROP(laT[i],"VIEW","Comment"))
ENDFOR
n = ADBOBJECTS(laT, "RELATION")
FOR i = 1 TO n
  lcRel = laT[i,1] + "|" + laT[i,2] + "|" + laT[i,3] + "|" + laT[i,4] + "|" + laT[i,5]
  FPUTS(lnH, "RELATION|" + lcRel)
ENDFOR
CLOSE DATABASES
nFree = ALINES(laFree, tcFree, 1, ",")
FOR i = 1 TO nFree
  lcT = laFree[i]
  USE (lcT) IN 0 SHARED ALIAS dumpfree
  SELECT dumpfree
  FPUTS(lnH, "FREETABLE|" + JUSTSTEM(lcT) + "|" + DBF() + "|" + TRANSFORM(RECCOUNT()))
  AFIELDS(laF, "dumpfree")
  FOR j = 1 TO ALEN(laF,1)
    FPUTS(lnH, "FIELD|" + laF[j,1] + "|" + laF[j,2] + "|" + TRANSFORM(laF[j,3]) + "|" + TRANSFORM(laF[j,4]) + "|" + IIF(laF[j,5],"Y","N"))
  ENDFOR
  FOR j = 1 TO TAGCOUNT()
    IF !EMPTY(TAG(j))
      FPUTS(lnH, "TAG|" + TAG(j) + "|" + KEY(j) + "|" + FOR(j) + "|" + IIF(PRIMARY(j),"PRIMARY",IIF(CANDIDATE(j),"CANDIDATE",IIF(UNIQUE(j),"UNIQUE","REGULAR"))) + "|" + IIF(DESCENDING(j),"DESC","ASC"))
    ENDIF
  ENDFOR
  USE IN dumpfree
ENDFOR
FCLOSE(lnH)
ON ERROR
RETURN "done"

PROCEDURE dumperr
LPARAMETERS tcMsg, tnLine
FPUTS(gnDumpH, "ERROR|" + tcMsg + "|line " + TRANSFORM(tnLine))
FCLOSE(gnDumpH)
ON ERROR
CANCEL
