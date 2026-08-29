namespace Contoso.Orders.Api.Models;

public class MovementRequest
{
    public string PartyId { get; set; } = string.Empty;

    public string Kind { get; set; } = string.Empty;

    public decimal Amount { get; set; }

    public string Currency { get; set; } = "USD";

    public string? Reference { get; set; }
}
