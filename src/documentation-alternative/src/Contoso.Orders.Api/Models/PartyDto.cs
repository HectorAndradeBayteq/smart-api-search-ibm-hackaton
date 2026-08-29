namespace Contoso.Orders.Api.Models;

public class PartyDto
{
    public string Id { get; set; } = string.Empty;

    public string Name { get; set; } = string.Empty;

    public string Doc { get; set; } = string.Empty;

    public string Segment { get; set; } = string.Empty;

    public string Status { get; set; } = string.Empty;

    public string? Email { get; set; }

    public DateOnly SinceDate { get; set; }
}
