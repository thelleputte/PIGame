# PIGame

Hello les zoulous

## GIT

# The super basics
Un petit tuto-lunch pour se (re-)familiariser avec Git(hub)
- first: https://guides.github.com/activities/hello-world/
- then: https://guides.github.com/introduction/flow/

# Working locally

Pour initier votre repository git en local, c'est ceci:
    
    cd /le-repertoire-parent-de-votre-repertoir-souhaité
    git clone https://github.com/thelleputte/PIGame.git votre-repertoire-souhaité
    
Une cheat sheet? C'est ici:

    https://services.github.com/kit/downloads/github-git-cheat-sheet.pdf
    
Mais en gros, ce qu'il faut retenir (une fois le répertoire initialisé en local sur votre machine), c'est que vous devez d'abord faire un "add" sur les fichiers que vous voulez que git suive. Si vous voulez qu'il suive tout, c'est alors:

    git add .
    
Ensuite, vous devez, en local, "valider" vos modifs (si vous étiez familier de subversion, c'est un peu comme faire un checkout, sauf que dans git, checkout a une autre signification (changer de branche de développement)). Pour ça, faut faire un "commit".

    git commit -m "j'explique en une ligne ce que j'ai modifié"
    
Ensuite, ça vous intéresse de rester en phase avec le repository central sur github. Pour ça vous voulez *d'abord* récupérer les modifs des autres. Ca se fait en deux étapes. D'abord les récupérer en local et vérifier qu'il n'y a pas de conflit entre ce que les autres ont fait et ce que vous avez fait, puis, si c'est bien ok, effectivement merger ce que les autres ont fait avec votre développement local.

    git fetch
    git pull
    
Si la première commande (fetch) vous signale une incompatibilité, deux solutions:
* Vous jugez que vous pouvez écraser vos changement en local (ça arrive parfois)
* Vous jugez que vous ne pouvez pas écraser vos changement en local

Dans le premier cas, c'est facile, vous faites:

    git fetch --all
    git reset origin/master

Dans le deuxième cas... c'est plus complexe, on avisera sur le moment même. :-) Mais franchement c'est pas fréquent.

A ce point-là, vous avez fait votre commit en local, vous avez récupéré l'info du repos central, vous avez mergé avec votre repos local. Vous voulez maintenant que les autres aient aussi accès à vos changements:

    git push
    
Et voilàààà pour les basics.


## BOOTSTRAP

La doc est dispo ici

    http://getbootstrap.com/getting-started/#download

## TRELLO

Pour la gestion de projet, Thib va créer un groupe sur Trello. Vous allez 
recevoir une invitation.

    http://www.trello.com

