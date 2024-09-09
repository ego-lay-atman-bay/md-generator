from .lines import Lines
import markdown
import bs4

class Document(Lines):
    block = True
    
    def write(self) -> str:
        return '\n\n'.join([str(section) for section in self])
    
    def to_html(self, use_ia = False) -> str:
        table_style = 'margin-bottom: 0; word-break: auto-phrase;'
        table_cell_style = 'word-break: auto-phrase;'
        table_header_style = 'background: #edecec;'
        code_style = 'padding: .2em .4em;; background-color: #e5e5e5; border-radius: 6px; white-space: break-spaces;'
        code_block_style = 'padding: 16px; line-height: 1.45; background-color: #f6f8fa; border-radius: 6px;'

        
        html = markdown.markdown(str(self), extensions = ['tables', 'fenced_code'])

        soup = bs4.BeautifulSoup(html, 'html.parser')
        # for code in soup.find_all('code'):
        #     if code.parent.name == 'pre':
        #         continue
        #     
        #     code['style'] = code.get('style', '') + code_style
        
        # for code in soup.find_all('pre'):
        #     code['style'] = code.get('style', '') + code_block_style
        
        if use_ia:
            for table in soup.find_all('table'):
                table.wrap(soup.new_tag('div', attrs = {'class': 'ui-accordion', 'style': 'margin-bottom: 20px;'}))
                table.wrap(soup.new_tag('div', attrs = {'class': 'ui-accordion-content table-responsive', 'style': 'padding: 0; border-top: 0;'}))
                
                table['style'] = table.get('style', '') + table_style
                table['class'] = 'table table-bordered table-striped table-hover'
                # table['stye'] = 'margin-bottom: revert;'
        
        # for table in soup.find_all('thead'):
            # table['style'] = 'font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;'
        
        if use_ia:
            for cell in soup.css.select('th, td'):
                cell['style'] = cell.get('style', '') + table_cell_style
                # cell['style'] = 'font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;'
        
        output_html = soup.decode(formatter = 'html5')
        
        return output_html
    
    IA_CSS = "https://archive.org/includes/build/css/archive.min.css"
