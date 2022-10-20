SELECT orders.DeliveryDate, Reference.Code as Reference, orders.CalculatedPendingQty
FROM [Order] orders
INNER JOIN Reference
ON Reference.Id = orders.ReferenceId
WHERE orders.Active = 1 AND orders.CalculatedPendingQty != 0