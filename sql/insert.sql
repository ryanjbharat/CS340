INSERT INTO Snakes (species, weight_lb, length, color, price)
VALUES ('Rattlesnake', 5, 10, 'beige', 100);

INSERT INTO Snakes (species, weight_lb, length, color, price)
VALUES ('King Cobra', 15, 20, 'red', 150);

INSERT INTO Snakes (species, weight_lb, length, color, price)
VALUES ('Green Snake', 3, 25, 'green', 95);

INSERT INTO Customers (first_name, last_name, address, city, state, postal, country, email)
VALUES ('Tim', 'Orentlikher', '123 Main St', 'Somewhere', 'NY', 10543, 'US', 'tim@snakesrus.com');

INSERT INTO Customers (first_name, last_name, address, city, state, postal, country, email)
VALUES ('Ash', 'Ketchum', '123 Poke Street', 'Pallet Town', 'IL', 50421, 'US', 'ash@ketchum.com');

INSERT INTO Customers (first_name, last_name, address, city, state, postal, country, email)
VALUES ('Harry', 'Potter', '56 Wizard Street', 'Hogwarts', 'FL', 52222, 'US', 'hp@hp.com');

INSERT INTO DeliveryPartners (organization_name, delivery_method)
VALUES ('Snakes On A Plane', 'Air');

INSERT INTO DeliveryPartners (organization_name, delivery_method)
VALUES ('Snakes On A Truck', 'Ground');

INSERT INTO DeliveryPartners (organization_name, delivery_method)
VALUES ('Snakes On A Boat', 'Boat');

INSERT INTO Breeders (breeder_name, email, phone_number)
VALUES( 'A1 Reptiles Inc', 'foo@bar.com', '0001112222');

INSERT INTO Breeders (breeder_name, email, phone_number)
VALUES( 'Big Reptiles 4 You', '4@u.com', '9605496502');

INSERT INTO Breeders (breeder_name, email, phone_number)
VALUES( 'Snake King', 'joe@snakeking.com', '6028540234');


INSERT INTO `SnakesBreeders` (`snake_id`, `breeder_id`) VALUES
(2, 2),
(3, 2),
(3, 3);

INSERT INTO `OrdersHeaders` (`order_id`, `customer_id`, `delivery_partner_id`, `order_date`, `shipped`) VALUES
(1, 2, 2, '2021-08-07', 0),
(2, 1, 3, '2021-08-07', 0),
(3, 3, 1, '2021-08-07', 0);


INSERT INTO `OrdersDetails` (`order_detail_id`, `order_id`, `snake_id`, `quantity`) VALUES
(1, 1, 1, 1),
(2, 1, 2, 1),
(3, 2, 3, 3),
(4, 3, 2, 1);


