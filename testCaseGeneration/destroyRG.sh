for rgname in `az group list --query "[? contains(name,'ZODIAC')][].{name:name}" -o tsv`; do
	echo Deleting ${rgname}
	az group delete -n ${rgname} --yes --no-wait
done

