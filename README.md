# Descripció del projecte
Aquest projecte consisteix en la creació d'un seqüenciador de passos que fa servir com a interfície un [Novation Launchpad Mini Mk3](https://novationmusic.com/products/launchpad-mini-mk3). 
Parteixo amb la base d'un projecte que havia començat, programat amb Python i la [Llibreria MIDO](https://mido.readthedocs.io/en/stable/index.html).

# Manual del projecte final
El manual es pot trobar [aquí](https://github.com/papertree1/launchpad-sequencer/blob/main/Launchpad%20Sequencer%20Manual.md)

# Base inicial
En l'estat inicial, el projecte té les següents funcionalitats implementades:
- Un seqüenciador de passos de llargada variable ($\leq$ 64) avança amb fins a dues veus amb alçada fixa
- Reflecteir l'estat del seqüenciador:
    - Pas actual
    - Veu visualitzada
    - Seqüència de la veu visualitzada
    - Tipus d'instrument (melòdic o no) amb diferents *layouts*
- Rebre input de l'usuari per a diferents accions:
    - Canviar la veu visualitzada
    - Editar passos de la seqüència (on/off)
    - Activar/pausar el seqüenciador
    - Tancar el programa

# Objectius
- Implementació de veus melòdiques
- Edició per pas d'alçada (*pitch*)
- Edició per pas de *velocity*
- Implementació de més de dues veus alhora
- [Implementació de diferents vistes](https://ibb.co/8r9Z7fH)
# Eines i recursos
- [Python 3](https://www.python.org/downloads/)
- [Llibreria MIDO per Python](https://mido.readthedocs.io/en/stable/index.html)
- [Llibreria asyncio per Python](https://docs.python.org/3/library/asyncio.html)
