-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 18, 2026 at 06:59 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `26fidoclouddb`
--

-- --------------------------------------------------------

--
-- Table structure for table `backuptb`
--

CREATE TABLE `backuptb` (
  `id` bigint(10) NOT NULL auto_increment,
  `UserName` varchar(250) NOT NULL,
  `Enckey` varchar(2000) NOT NULL,
  `pubkey` varchar(500) NOT NULL,
  `prikey2` varchar(500) NOT NULL,
  `Qrcode` varchar(250) NOT NULL,
  `Hash1` varchar(500) NOT NULL,
  `Hash2` varchar(500) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `backuptb`
--

INSERT INTO `backuptb` (`id`, `UserName`, `Enckey`, `pubkey`, `prikey2`, `Qrcode`, `Hash1`, `Hash2`) VALUES
(1, 'san', '04523672c65fdf09b1a10265a2b123beab249a42b2c4c9a28de64a6b2f92956f621dff5e44a4bc44bd4026036a43eac80197b2fe316906b4ab9272b59b5ec2992e10b3d4ec10f676d8c89864d94a29cf915ce660c0c13e1e3febdddd37cd88046553c18ef0e4738831da47729727cf8959f8089008fcf71be298f5b1e30ab180dd06748f9f0ef9c1b007faa8324566b565eb17a7e1bc1bf581d25281393e3043f9', '0270b4002726b57262f5d522ed80b22d1998b036f772cd84db1dc12bddc72a923f', '212eea8fff1db8c571afd14e5da12c7ecaee04908b5daf331a4ddd82bf9dbd48', '9086.png', '0', '14D1C2E62E49A612147316294B70AD733E47B6A2637A7145812123BD732F30EE');

-- --------------------------------------------------------

--
-- Table structure for table `filetb`
--

CREATE TABLE `filetb` (
  `id` bigint(20) NOT NULL auto_increment,
  `OwnerName` varchar(250) NOT NULL,
  `FileInfo` varchar(500) NOT NULL,
  `FileName` varchar(250) NOT NULL,
  `Pukey` varchar(250) NOT NULL,
  `Pvkey` varchar(250) NOT NULL,
  `hash1` varchar(250) NOT NULL,
  `hash2` varchar(250) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `filetb`
--

INSERT INTO `filetb` (`id`, `OwnerName`, `FileInfo`, `FileName`, `Pukey`, `Pvkey`, `hash1`, `hash2`) VALUES
(1, 'san', 'myfile', '9071tamil8.txt', '03ff3d4bfc92b24d1b2cbd9cc8063a44fdad23d2053d86ad49d8e188d005d80ec4', '2699f7ed86886b7fdf18b2bc02aec5a56432171a9ee7e6a1983914ec65698206', '0', '70299F04FEE71A1809B77628C88DA5E1CDB7AD2DD50EAFE90B59A7DEBF9BFB1F');

-- --------------------------------------------------------

--
-- Table structure for table `regtb`
--

CREATE TABLE `regtb` (
  `id` bigint(20) NOT NULL auto_increment,
  `Name` varchar(250) NOT NULL,
  `Mobile` varchar(250) NOT NULL,
  `Email` varchar(250) NOT NULL,
  `Address` varchar(500) NOT NULL,
  `UserName` varchar(250) NOT NULL,
  `Password` varchar(250) NOT NULL,
  `Status` varchar(250) NOT NULL,
  `Pubkey` varchar(250) NOT NULL,
  `Prikey` varchar(250) NOT NULL,
  `prikey1` varchar(250) NOT NULL,
  `prikey2` varchar(250) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `regtb`
--

INSERT INTO `regtb` (`id`, `Name`, `Mobile`, `Email`, `Address`, `UserName`, `Password`, `Status`, `Pubkey`, `Prikey`, `prikey1`, `prikey2`) VALUES
(1, 'sangeeth Kumar', '9486365535', 'sangeeth5535@gmail.com', 'No 16, Samnath Plaza, Madurai Main Road, Melapudhur', 'san', 'san', 'Approved', '0270b4002726b57262f5d522ed80b22d1998b036f772cd84db1dc12bddc72a923f', 'b63605a25d18bc971d4590888255bea2da31aa0c5046a6e3be3b31d527e5d3cc', '9718ef2da20504526cea41c6dff492dc10dfae9cdb1b09d0a476ec5798786e84', '212eea8fff1db8c571afd14e5da12c7ecaee04908b5daf331a4ddd82bf9dbd48');

-- --------------------------------------------------------

--
-- Table structure for table `temptb`
--

CREATE TABLE `temptb` (
  `id` bigint(10) NOT NULL auto_increment,
  `UserName` varchar(250) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=13 ;

--
-- Dumping data for table `temptb`
--

INSERT INTO `temptb` (`id`, `UserName`) VALUES
(1, 'sanuser'),
(2, 'sanuser'),
(3, 'sanuser'),
(4, 'sanuser'),
(5, 'sanuser'),
(6, 'san'),
(7, 'san'),
(8, 'san'),
(9, 'san'),
(10, 'san'),
(11, 'san'),
(12, 'san');
