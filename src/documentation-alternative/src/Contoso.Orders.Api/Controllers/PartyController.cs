using Contoso.Orders.Api.Data;
using Contoso.Orders.Api.Models;
using Microsoft.AspNetCore.Mvc;

namespace Contoso.Orders.Api.Controllers;

[ApiController]
[Route("api/v1/parties")]
public class PartyController : ControllerBase
{
    private readonly PartyStore _store;

    public PartyController(PartyStore store)
    {
        _store = store;
    }

    [HttpGet("{id}")]
    public IActionResult Get(string id)
    {
        var item = _store.Find(id);

        if (item is null)
        {
            return NotFound(new ErrorDto { Code = "PARTY_NOT_FOUND", Message = "Party does not exist." });
        }

        return Ok(item);
    }

    [HttpGet]
    public IActionResult GetList([FromQuery] string? segment, [FromQuery] string? status, [FromQuery] int page = 1, [FromQuery] int size = 20)
    {
        if (page < 1 || size < 1 || size > 100)
        {
            return BadRequest(new ErrorDto { Code = "INVALID_PAGING", Message = "page >= 1 and size between 1 and 100." });
        }

        var all = _store.Search(segment, status);

        var result = new PagedResult<PartyDto>
        {
            Items = all.Skip((page - 1) * size).Take(size).ToList(),
            Page = page,
            Size = size,
            Total = all.Count
        };

        return Ok(result);
    }

    [HttpGet("lookup")]
    public IActionResult Lookup([FromQuery] string doc)
    {
        if (string.IsNullOrWhiteSpace(doc))
        {
            return BadRequest(new ErrorDto { Code = "DOC_REQUIRED", Message = "doc is required." });
        }

        var item = _store.FindByDoc(doc);

        if (item is null)
        {
            return NotFound(new ErrorDto { Code = "PARTY_NOT_FOUND", Message = "Party does not exist." });
        }

        return Ok(item);
    }

    [HttpPatch("{id}")]
    public IActionResult Patch(string id, [FromBody] PartyPatchRequest request)
    {
        var item = _store.Patch(id, request);

        if (item is null)
        {
            return NotFound(new ErrorDto { Code = "PARTY_NOT_FOUND", Message = "Party does not exist." });
        }

        return Ok(item);
    }
}
