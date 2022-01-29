-- Table structure for table `users`
--
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `category` varchar(50) NOT NULL,
    `name` varchar(50) NOT NULL,
    `email` varchar(50) NOT NULL,
    `username` varchar(25) NOT NULL,
    `password` varchar(100) NOT NULL,
    'code' varchar(100) NOT NULL,
    'status' varchar(100) DEFAULT 'NO',
    `mobile` varchar(20) NOT NULL,
    `reg_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `online` varchar(1) NOT NULL DEFAULT '0',
    `activation` varchar(3) NOT NULL DEFAULT 'yes',
    PRIMARY KEY (`id`)
) ENGINE = MyISAM AUTO_INCREMENT = 16 DEFAULT CHARSET = latin1;
--
-- feedback form
DROP TABLE IF EXISTS `feedback`;
CREATE TABLE IF NOT EXISTS `feedback` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `email` varchar(50) NOT NULL,
    `text` varchar(30) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = MyISAM AUTO_INCREMENT = 16 DEFAULT CHARSET = latin1;
-- admin
DROP TABLE IF EXISTS `admin`;
CREATE TABLE IF NOT EXISTS `admin` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `firstName` varchar(125) NOT NULL,
    `lastName` varchar(125) NOT NULL,
    `email` varchar(100) NOT NULL,
    `mobile` varchar(25) NOT NULL,
    `address` text NOT NULL,
    `password` varchar(100) NOT NULL,
    `type` varchar(20) NOT NULL,
    `confirmCode` varchar(10) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB AUTO_INCREMENT = 5 DEFAULT CHARSET = latin1;
--
-- Table structure for table `products`
--
DROP TABLE IF EXISTS `products`;
CREATE TABLE IF NOT EXISTS `products` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `pName` varchar(100) NOT NULL,
    `price` int(11) NOT NULL,
    `description` text NOT NULL,
    `available` int(11) NOT NULL,
    `category` varchar(100) NOT NULL,
    `item` varchar(100) NOT NULL,
    `pCode` varchar(20) NOT NULL,
    `picture` text NOT NULL,
    `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB AUTO_INCREMENT = 22 DEFAULT CHARSET = latin1;
--
-- Dumping data for table `products`
--