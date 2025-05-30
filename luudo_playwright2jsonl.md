```mermaid
flowchart TD
    A([Start]) --> B[Start Playwright codegen and WatchHandler]
    B --> C[/Initialize tracking variables:<br/>- number_of_all_current_lines = 0<br/>- last_content_hash = None/]
    
    C --> D[Start monitoring temporary JSONL file]
    
    subgraph PlaywrightAndWatcher["Playwright Test and WatchHandler"]
        E[Run test and interact with web] --> F[/Generate and save JSONL flow to temp file/]
        F --> G{File change detected?}
        G -- No --> E
        G -- Yes --> H[/Check content hash/]
        H --> I{Hash changed?}
        I -- No --> E
        I -- Yes --> J[/Count current lines/]
        
        J --> K{Compare line count}
        K -- Lines increased --> L[/Read newly added lines/]
        L --> M[Format new lines according to JSONL standard]
        M --> N[/Append to target JSONL file/]
        
        K -- Line count unchanged --> O{Only last line changed?}
        O -- Yes --> P[/Remove last line from target file/]
        P --> Q[Reformat last line]
        Q --> R[/Add formatted line to target file/]
        
        O -- No --> S([Do nothing])
        
        K -- Lines decreased --> T[/Rewrite entire target file/]
        
        N --> U[/Update tracking variables/]
        R --> U
        S --> U
        T --> U
        
        U --> V{Continue testing?}
        V -- Yes --> E
        V -- No --> W([End])
    end
    
    D --> PlaywrightAndWatcher
    W --> X([End program])
