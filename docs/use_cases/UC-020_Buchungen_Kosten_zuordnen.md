Als Admin möchte ich sehen können wieviel von meinem Budget bereits verbraucht ist. Dazu muss ich den Buchungen Kosten zuordnen können. Die Berechnung ist der Kosten hängt aber vom Task Typ ab. Daher würde ich diesen Use case in drei Steps umsetzen wollen.
a) Buchungen vom Typ "Client Utilized" kosten zuordnen
b) Buchungen vom Typ "Overtime" Kosten zuordnen 
c) Buchungen vom Typ "On Call" Kosten zuordnen können

Buchungen vom Typ "Client Utilized"
Für die Berechnung brauchen wir aus der Buchung das Buchungsdatum, den Buchungsnamen und die Anzahl der Stunden.
Anhand des Buchungsnamen ermitteln wir den entsprechenden Mitarbeiter-Datensatz und holen uns aus diesem den am Buchungsdatum gültigen Kosten für diese Gehaltsgruppe und mulitiplizieren diese mit den Stunden. 