using Contoso.Orders.Api.Data;
using Contoso.Orders.Api.Models;
using Microsoft.AspNetCore.Mvc;

namespace Contoso.Orders.Api.Controllers;

[ApiController]
[Route("api/v1/movements")]
public class MovementController : ControllerBase
{
    private readonly MovementStore _store;
    private readonly PartyStore _parties;

    public MovementController(MovementStore store, PartyStore parties)
    {
        _store = store;
        _parties = parties;
    }

    [HttpPost]
    public IActionResult Post([FromBody] MovementRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.PartyId) || _parties.Find(request.PartyId) is null)
        {
            return BadRequest(new ErrorDto { Code = "PARTY_NOT_FOUND", Message = "partyId does not exist." });
        }

        if (request.Amount <= 0)
        {
            return BadRequest(new ErrorDto { Code = "INVALID_AMOUNT", Message = "amount must be greater than zero." });
        }

        if (request.Kind is not ("charge" or "refund" or "adjustment"))
        {
            return BadRequest(new ErrorDto { Code = "INVALID_KIND", Message = "kind must be charge, refund or adjustment." });
        }

        var item = _store.Create(request);

        return Created($"/api/v1/movements/{item.Id}", item);
    }

    [HttpGet("{id}")]
    public IActionResult Get(string id)
    {
        var item = _store.Find(id);

        if (item is null)
        {
            return NotFound(new ErrorDto { Code = "MOVEMENT_NOT_FOUND", Message = "Movement does not exist." });
        }

        return Ok(item);
    }

    [HttpGet]
    public IActionResult GetByParty([FromQuery] string partyId)
    {
        if (string.IsNullOrWhiteSpace(partyId))
        {
            return BadRequest(new ErrorDto { Code = "PARTY_REQUIRED", Message = "partyId is required." });
        }

        return Ok(_store.ByParty(partyId));
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(string id)
    {
        var item = _store.Cancel(id);

        if (item is null)
        {
            return Conflict(new ErrorDto { Code = "NOT_CANCELLABLE", Message = "Movement does not exist or is not pending." });
        }

        return Ok(item);
    }
}
