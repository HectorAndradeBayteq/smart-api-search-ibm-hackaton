using Contoso.Orders.Api.Models;

namespace Contoso.Orders.Api.Data;

public class PartyStore
{
    private readonly Dictionary<string, PartyDto> _items = new(StringComparer.OrdinalIgnoreCase);

    public PartyStore()
    {
        Add("P-1001", "Marta Sánchez", "27461829", "retail", "active", "marta.sanchez@example.com", new DateOnly(2019, 3, 14));
        Add("P-1002", "Andes Logística S.A.", "9004512331", "corporate", "active", "cuentas@andeslog.example", new DateOnly(2021, 8, 2));
        Add("P-1003", "Julián Ortega", "18734920", "retail", "blocked", null, new DateOnly(2017, 11, 30));
        Add("P-1004", "Delta Retail SpA", "7701223349", "corporate", "active", "finanzas@deltaretail.example", new DateOnly(2022, 1, 19));
    }

    private void Add(string id, string name, string doc, string segment, string status, string? email, DateOnly since)
    {
        _items[id] = new PartyDto
        {
            Id = id,
            Name = name,
            Doc = doc,
            Segment = segment,
            Status = status,
            Email = email,
            SinceDate = since
        };
    }

    public PartyDto? Find(string id)
    {
        return _items.TryGetValue(id, out var item) ? item : null;
    }

    public PartyDto? FindByDoc(string doc)
    {
        return _items.Values.FirstOrDefault(x => x.Doc == doc);
    }

    public IReadOnlyList<PartyDto> Search(string? segment, string? status)
    {
        return _items.Values
            .Where(x => segment is null || x.Segment.Equals(segment, StringComparison.OrdinalIgnoreCase))
            .Where(x => status is null || x.Status.Equals(status, StringComparison.OrdinalIgnoreCase))
            .OrderBy(x => x.Id)
            .ToList();
    }

    public PartyDto? Patch(string id, PartyPatchRequest request)
    {
        var item = Find(id);

        if (item is null)
        {
            return null;
        }

        if (request.Email is not null)
        {
            item.Email = request.Email;
        }

        if (request.Segment is not null)
        {
            item.Segment = request.Segment;
        }

        return item;
    }
}
