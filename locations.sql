-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Erstellungszeit: 10. Nov 2026 um 00:37
-- Server-Version: 10.11.11-MariaDB
-- PHP-Version: 8.2.35

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `christian`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `locations`
--

CREATE TABLE `locations` (
  `ID` int(11) NOT NULL,
  `Name` text CHARACTER SET latin1 COLLATE latin1_german1_ci NOT NULL,
  `Beschreibung` text CHARACTER SET latin1 COLLATE latin1_german1_ci NOT NULL,
  `latitude` float NOT NULL,
  `longitude` float NOT NULL,
  `Link` tinytext CHARACTER SET latin1 COLLATE latin1_german1_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

--
-- Daten für Tabelle `locations`
--

INSERT INTO `locations` (`ID`, `Name`, `Beschreibung`, `latitude`, `longitude`, `Link`) VALUES
(1, 'Fernsehturm Berlin', 'hoch', 52.5208, 13.4094, 'test'),
(2, 'test', 'toll', 51.525, 9.93027, 'www.uhrzeit.de'),
(3, 'wrert', 'fhg', 52.4172, 13.0588, 'jhg'),
(4, 'sdf', 'sdf', 52.2427, 11.8059, 'sdf'),
(5, 'we', 'wew', 51.7829, 13.2787, 'we'),
(6, 'sfs', 'ssssss', 52.4525, 13.378, 'ffffff'),
(7, 'Fernsehturm ', 'im Zentrum Berlins', 52.5208, 13.4094, 'www.uhrzeit.de'),
(8, 'Berliner Dom', 'Mitten in der Stadt', 52.5191, 13.4012, 'Später mehr'),
(9, 'Zuhause in der Uckermark', 'Ein ruhiges Plätzchen zum ausruhen', 53.1637, 13.9689, 'Später kommt der Link dazu'),
(10, 'werwerwerwerwer', 'toll', 51.525, 9.93027, 'www.uhrzeit.de'),
(11, 'Fernsehturm', 'im Zentrum Berlins', 52.5208, 13.4094, 'https://tv-turm.de/'),
(12, 'trstsdf', 'ddfgdf', 52.451, 13.3938, ''),
(13, 'ewrtetr', 'werw', 52.4024, 13.3596, ''),
(14, 'ertert', 'wew', 51.7829, 13.2787, 'we'),
(15, 'erterteter', '', 51.6343, 12.3149, ''),
(16, 'test', '', 52.4381, 13.6499, ''),
(17, 'test', '', 52.4381, 13.6499, '');

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `locations`
--
ALTER TABLE `locations`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `locations`
--
ALTER TABLE `locations`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
