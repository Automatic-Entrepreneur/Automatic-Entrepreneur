HEAD = """<!doctype html>
<html>
	<head>
		<meta charset='UTF-8'>
		<title>{name} Summary</title>
		<style>
			.divider {{
				border-top: medium solid #1E1E1E;
			}}
			.only-print {{
				margin-right:250px;
				margin-left:250px;
            }}
			@media print {{
				.only-print {{
					margin-right:0px;
					margin-left:0px;
				}}
				.hide-print-button {{
					visibility:hidden;
				}}
			}}
			.grid-container	{{
				display: grid;
				grid-template-columns: auto auto auto auto auto;
				padding: 0px;
			}}
			.grid-item	{{
				padding: 10px;
				text-align: center;
			}}
		</style>
		<link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
	</head>
	<body class='only-print' style="font-family: 'Roboto', sans-serif">
		<div style="display:flex;justify-content:space-between">
				<div>
					<h1>
						<a href="https://{website}">
"""
TITLE_P = """						<img src='{logo}' style='height:60px;position:relative;top:20px'></a>    {name} Summary
"""
TITLE_N = """						{name} Summary
"""
LOGO = """					</h1>
				</div>
				<div style="font-size:20px">
					<h3>
						<span style='color:#4285F4'>A</span>
						<span style='color:#DB4437'>u</span>
						<span style='color:#F4B400'>t</span>
						<span style='color:#0F9D58'>o</span>
						<span style='color:#DB4437'>m</span>
						<span style='color:#4285F4'>a</span>
						<span style='color:#F4B400'>t</span>
						<span style='color:#0F9D58'>i</span>
						<span style='color:#DB4437'>c</span>
						<span style='color:#F4B400'>E</span>
						<span style='color:#DB4437'>n</span>
						<span style='color:#F4B400'>t</span>
						<span style='color:#4285F4'>r</span>
						<span style='color:#F4B400'>e</span>
						<span style='color:#0F9D58'>p</span>
						<span style='color:#DB4437'>r</span>
						<span style='color:#F4B400'>e</span>
						<span style='color:#0F9D58'>n</span>
						<span style='color:#F4B400'>e</span>
						<span style='color:#DB4437'>u</span>
						<span style='color:#4285F4'>r</span>
					</h3>
				</div>
		</div>

		<div style="position:relative;top:-15px">
			<hr>
			<div class="grid-container" style="position:relative;top:-5px">
"""
FACTS = [
    """				<div class="grid-item">{data}</div>""",
    """				<div class="grid-item">{data}</div>""",
    """				<div class="grid-item">Founded in {data}</div>""",
    """				<div class="grid-item">Glassdoor rating: {data}</div>""",
    """				<div class="grid-item">CEO: {data}</div>""",
]
MAIN = """			</div>
		</div>
		<div style="margin-right:10px;margin-left:10px">
"""
MISSION = """			<div>
				<p style="font-size:18px;text-align:center">
					{mission}
				</p>
			</div>
"""
REPORT = """			<div>
				<h2>
					Company report
				</h2>
				<hr class="divider" style="margin-left:0;max-width:100px">
				<p>
					{report}
				</p>
				<p style="font-style:italic">
					<a href="https://find-and-update.company-information.service.gov.uk/company/{id}/filing-history">Read the full report here</a>
				</p>
				<hr class="divider">
			</div>
"""
FINANCE_OPEN = """			<div>
				<h2>
					Finance overview
				</h2>
				<hr class="divider" style="margin-left:0;max-width: 100px">
"""
GRAPHS_OPEN = """				<h3>Asset graphs</h3>
				<div>
"""
IMAGE_L = """					<div style='display:flex'>
						<img src={img} alt={img} width='500'>
						<div style="width:400px">
							<p style="font-weight:bold">Highlights:</p>
							{caption}
						</div>
					</div>
"""
IMAGE_R = """					<div style='display:flex'>
						<div style="text-align:right;width:400px">
							<p style="font-weight:bold">Highlights:</p>
							{caption}
                        </div>
						<img src={img} alt={img} width='500'>
					</div>
"""
GRAPHS_CLOSE = """				</div>
				<br>
"""
STOCK_OPEN = """				<h3>Stock breakdown</h3>
				<div>
"""
STOCK = """				
						<h4> Daily Stock Information </h4>
    
					<table>
						<tr>
							<td> <b>Name</b></td>
							<td>{name}</td>
						</tr>
						<tr>
							<td><b>Symbol</b></td>
							<td>{symbol}</td>
						</tr>
						<tr>
							<td><b>Exchange</b></td>
							<td>{exchange}</td>
						</tr>
						<tr>
							<td><b>Currency</b></td>
							<td>{currency}</td>
						</tr>
						<tr>
							<td><b>Price</b></td>
							<td>{price}</td>
						</tr>
						<tr>
							<td><b>Trade Volume</b></td>
							<td>{tradevol}</td>
						</tr>
						<tr>
							<td><b>Change</b></td>
							<td>{change}</td>
						</tr>
						<tr>
							<td><b>52 Week High</b></td>
							<td>{_52hi}</td>
						</tr>
						<tr>
							<td><b>52 Week Low</b></td>
							<td>{_52lo}</td>
						</tr>
						<tr>
							<td><b>50 Day Average</b></td>
							<td>{_50ave}</td>
						</tr>
						<tr>
							<td><b>200 Day Average</b></td>
							<td>{_200ave}</td>
						</tr>
					</table>
					
					<h4> Other Financial Information </h4>
						
					<table>
						<tr>
							<td> <b>Market Cap</b></td>
							<td>{marketcap}</td>
						</tr>
						<tr>
							<td><b>EBITDA</b></td>
							<td>{ebitda}</td>
						</tr>
						<tr>
							<td><b>PERatio</b></td>
							<td>{peratio}</td>
						</tr>
						<tr>
							<td><b>PEGRatio</b></td>
							<td>{pegratio}</td>
						</tr>
						<tr>
							<td><b>Book Value</b></td>
							<td>{bookval}</td>
						</tr>
						<tr>
							<td><b>Profit Margin</b></td>
							<td>{profitmargin}</td>
						</tr>
						
					</table>
"""
STOCK_ONLY = """<h4> Daily Stock Information </h4>
    
					<table>
						<tr>
							<td><b>Symbol</b></td>
							<td>{symbol}</td>
						</tr>
						<tr>
							<td><b>High (Day)</b></td>
							<td>{hi}</td>
						</tr>
						<tr>
							<td><b>Low (Day)</b></td>
							<td>{lo}</td>
						</tr>
						<tr>
							<td><b>Price</b></td>
							<td>{price}</td>
						</tr>
						<tr>
							<td><b>Trade Volume</b></td>
							<td>{tradevol}</td>
						</tr>
						<tr>
							<td><b>Change</b></td>
							<td>{change}</td>
						</tr>
						
					</table>
"""
TABLE = """				<h3>Finance Information</h3>
									{table}
"""
STOCK_CLOSE = """				</div>
"""
FINANCE_CLOSE = """			</div>
				<hr class="divider">
"""
SAYING_OPEN = """			<div>
				<h2>
					What people are saying
				</h2>
				<hr class="divider" style="margin-left:0;max-width: 100px">
"""
SATISFACTION_OPEN = """				<div>
					<h3>Employee satisfaction at {name}</h3>
"""
SATISFACTION_CLOSE = """					</div>
"""
DIVIDER = """					<hr class="divider" style="margin-left:0;max-width: 100px">
"""
NEWS_OPEN = """					<h3>{name} in the news</h3>
					<div>
"""
NEWS = """					<div>
						{title} ({date})
						| <i>{author}, {publisher}</i> (<a href={link}>read</a>)
						<hr style="border-top:thin solid #1E1E1E">
					</div>
"""
SENTIMENT = "					<b>Overall news sentiment: {pos}% positive</b>"
NEWS_CLOSE = """				</div>
"""
SAYING_CLOSE = """				<hr class="divider">
			</div>
"""
FAQS_OPEN = """			<div>
				<h3>FAQs</h3>
"""
FAQS_CLOSE = """			</div>
"""
SOCIALS_OPEN = """			<br><br>
			<div>
				<hr class="divider">
				<div style="display:flex;justify-content:space-between">
					<div style="display:flex;align-items:baseline">
"""
SOCIALS = """						<a href="{data}"><img src="{image}" alt="social media icon" height="20"></a>&nbsp;&nbsp;
"""
WEBSITE = """						<p style="position:relative;top:-5px">&nbsp;|&nbsp;&nbsp;website: <a href="https://{website}">{website}</a></p>
"""
SOCIALS_CLOSE = """					</div>
					<div style="position:relative;top:10px">
						Generated @ {time}<p style="display:inline" class="hide-print-button"> | </p>
						<a href='javascript:if(window.print)window.print()' class="hide-print-button">create pdf</a>
					</div>
				</div>
			</div>			
		</div>
	</body>
</html>"""
