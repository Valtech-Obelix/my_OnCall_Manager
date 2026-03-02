# UC-013 – Schichtverteilung nach Standort anzeigen

## Version
0.1

---

## Ziel

Als Admin  
möchte ich verfolgen können, wie sich die Verteilung der Schichten zwischen den Standorten entwickelt,  
um die Entwicklung in die gewünschte Richtung beeinflussen zu können.

---

## Hauptablauf

1. Admin öffnet den Dialog „Schichtverteilung nach Standort“.
2. System setzt den Betrachtungszeitraum standardmäßig auf `13` Wochen.
3. Admin passt bei Bedarf die Anzahl der Wochen an.
4. System zeigt die Auswertung als gestapeltes Säulendiagramm je Woche und Standort.
5. Admin schließt den Dialog über die Buttonleiste mit `Schließen`.

---

## Akzeptanzkriterien

- Der Dialog ist als eigener Dialog über das Hauptfenster erreichbar.
- Das Eingabefeld für den Betrachtungszeitraum ist vorhanden.
- Standardwert beim Öffnen ist `13` Wochen.
- Unterhalb des Eingabefelds wird ein gestapeltes Säulendiagramm angezeigt.
- Das Diagramm zeigt die Verteilung der Schichten pro Woche und Standort.
- Unterhalb des Diagramms ist eine Buttonleiste mit mindestens dem Button `Schließen` vorhanden.
