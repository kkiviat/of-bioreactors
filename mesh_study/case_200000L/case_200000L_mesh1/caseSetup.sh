grep -v "<" PyFoamPrepareCaseParameters > tmpfile && mv tmpfile PyFoamPrepareCaseParameters
grep -v "=" PyFoamPrepareCaseParameters > tmpfile && mv tmpfile PyFoamPrepareCaseParameters
rm 0/*.template
setFields
