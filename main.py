# -*- coding: utf-8 -*-
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from usecase.logger.logreader.logreader import InventoryLogReader, MoneyLogReader
    from usecase.logger.logwriter.logwriter import CombinedLogWriter, OutputWriter
    from usecase.logger.core import LogProcessor
except ImportError as e:
    print("Import error: %s" % str(e))
    print("Current sys.path: %s" % sys.path)
    sys.exit(1)
def main():
    default_inventory_file = os.path.join('sources_files', 'inventory_logs.txt')
    default_money_file = os.path.join('sources_files', 'money_logs.txt')
    
    if len(sys.argv) == 1:
        inventory_file = default_inventory_file
        money_file = default_money_file
    elif len(sys.argv) == 3:
        inventory_file = sys.argv[1]
        money_file = sys.argv[2]
    else:
        print("Usage: python main.py")
        print("Or: python main.py inventory_logs.txt money_logs.txt")
        return
    
    if not os.path.exists(inventory_file):
        print("File %s not found" % inventory_file)
        print("Please make sure files are in sources_files folder")
        return
        
    if not os.path.exists(money_file):
        print("File %s not found" % money_file)
        print("Please make sure files are in sources_files folder")
        return
    
    inventory_reader = InventoryLogReader()
    money_reader = MoneyLogReader()
    combined_writer = CombinedLogWriter()
    output_writer = OutputWriter()
    
    processor = LogProcessor(inventory_reader, money_reader, combined_writer, output_writer)
    
    try:
        print("Reading logs...")
        inventory_logs = inventory_reader.read_logs(inventory_file)
        money_logs = money_reader.read_logs(money_file)
        
        print("Processing logs...")
        processor.process_logs(inventory_logs, money_logs)
        
        print("Creating combined log...")
        combined_logs = processor.create_combined_logs()
        combined_writer.write_logs(combined_logs, 'combined_log.txt')

        print("Generating statistics...")
        stats = processor.generate_statistics()
        output_writer.write_output(stats, 'output.txt')
        
        print("Starting interactive mode...")
        processor.interactive_mode()
        
        print("\nProcessing completed!")
        print("Results saved to combined_log.txt and output.txt")
        
    except Exception as e:
        print("Error occurred: %s" % str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()