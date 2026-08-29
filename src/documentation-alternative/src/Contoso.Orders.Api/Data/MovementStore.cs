using Contoso.Orders.Api.Models;

namespace Contoso.Orders.Api.Data;

public class MovementStore
{
    private readonly List<MovementDto> _items = [];
    private int _seq = 500;

    public MovementDto Create(MovementRequest request)
    {
        var item = new MovementDto
        {
            Id = "M-" + (++_seq),
            PartyId = request.PartyId,
            Kind = request.Kind,
            Amount = request.Amount,
            Currency = request.Currency,
            State = "pending",
            CreatedAt = DateTimeOffset.UtcNow
        };

        _items.Add(item);
        return item;
    }

    public MovementDto? Find(string id)
    {
        return _items.FirstOrDefault(x => x.Id.Equals(id, StringComparison.OrdinalIgnoreCase));
    }

    public IReadOnlyList<MovementDto> ByParty(string partyId)
    {
        return _items.Where(x => x.PartyId.Equals(partyId, StringComparison.OrdinalIgnoreCase)).ToList();
    }

    public MovementDto? Cancel(string id)
    {
        var item = Find(id);

        if (item is null || item.State != "pending")
        {
            return null;
        }

        item.State = "cancelled";
        return item;
    }
}
