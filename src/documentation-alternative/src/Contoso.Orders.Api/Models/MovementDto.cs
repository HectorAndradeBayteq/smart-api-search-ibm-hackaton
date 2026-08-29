namespace Contoso.Orders.Api.Models;

public class MovementDto
{
    public string Id { get; set; } = string.Empty;

    public string PartyId { get; set; } = string.Empty;

    public string Kind { get; set; } = string.Empty;

    public decimal Amount { get; set; }

    public string Currency { get; set; } = "USD";

    public string State { get; set; } = string.Empty;

    public DateTimeOffset CreatedAt { get; set; }
}
