CREATE TABLE Snakes(
    snake_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    species VARCHAR(50) NOT NULL,
    weight_lb INT NOT NULL,
    length DOUBLE(6,2) NOT NULL,
    color VARCHAR(20) NOT NULL,
    price DOUBLE(6,2) NOT NULL
);
    
CREATE TABLE Customers(
    customer_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	address VARCHAR(50) NOT NULL,
	city VARCHAR(50) NOT NULL,
	state VARCHAR(2) NOT NULL,
	postal VARCHAR(10) NOT NULL, 
	country VARCHAR(50) NOT NULL, 
	email VARCHAR(50) UNIQUE
);
  
CREATE TABLE DeliveryPartners(
    delivery_partner_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
	organization_name VARCHAR(50) NOT NULL,
	delivery_method VARCHAR(20) NOT NULL
);

CREATE TABLE Breeders(
    breeder_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    breeder_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    phone_number VARCHAR(10)
);

CREATE TABLE SnakesBreeders(
    snake_id INT NOT NULL,
    breeder_id INT NOT NULL,
    PRIMARY KEY (snake_id, breeder_id),
    FOREIGN KEY (snake_id) REFERENCES Snakes(snake_id) ON DELETE CASCADE,
    FOREIGN KEY (breeder_id) REFERENCES Breeders(breeder_id) ON DELETE CASCADE
);

CREATE TABLE OrdersHeaders(
	order_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    customer_id INT NOT NULL,
    delivery_partner_id INT NOT NULL,
    order_date DATE NOT NULL,
    shipped BOOLEAN DEFAULT False,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (delivery_partner_id) REFERENCES DeliveryPartners(delivery_partner_id)
);

CREATE TABLE OrdersDetails(
    order_detail_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    order_id INT NOT NULL,
    snake_id INT NOT NULL,
    quantity INT UNSIGNED NOT NULL,
    FOREIGN KEY (order_id) REFERENCES OrdersHeaders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (snake_id) REFERENCES Snakes(snake_id)
);