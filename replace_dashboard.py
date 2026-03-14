import urllib.request
# Télécharger depuis pastebin ou juste écraser avec le contenu
print("Méthode : exécutez python replace_dashboard.py")
```

---

**La méthode la plus simple** : dans VS Code ou votre éditeur, ouvrez `src\ui\tabs\dashboard_tab.py`, **Ctrl+A**, effacez tout, puis collez le code que je vous ai fourni dans ma réponse précédente (le grand bloc de code entre les balises du fichier créé).

Ensuite vérifiez :
```
python -c "import ast; ast.parse(open('src/ui/tabs/dashboard_tab.py', encoding='utf-8').read()); print('Syntaxe OK')"