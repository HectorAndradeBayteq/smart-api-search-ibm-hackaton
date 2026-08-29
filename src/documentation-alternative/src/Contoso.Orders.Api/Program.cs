using Contoso.Orders.Api.Data;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddSingleton<PartyStore>();
builder.Services.AddSingleton<MovementStore>();

var app = builder.Build();

app.UseMiddleware<Contoso.Orders.Api.TokenMiddleware>();
app.MapControllers();

app.Run();
