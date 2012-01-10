/* Albert Navas Mallo
   hisi46997513*/
   
DROP TABLE ram;
DROP TABLE swap;
DROP TABLE discs;
DROP TABLE usuaris;
DROP TABLE cpu;
DROP TABLE pcs;

-- -----------------------------------------------------
-- Table ram
-- -----------------------------------------------------
CREATE TABLE ram (
  id_pc_ram serial NOT NULL ,
  id_pc VARCHAR(45) NULL ,
  total VARCHAR(45) NULL ,
  used VARCHAR(45) NULL ,
  free VARCHAR(45) NULL ,
  shared VARCHAR(45) NULL ,
  buffers VARCHAR(45) NULL ,
  cached VARCHAR(45) NULL ,
  timereg VARCHAR(45) NULL ,
  dayreg VARCHAR(45) NULL ,
  PRIMARY KEY (id_pc_ram) );



-- -----------------------------------------------------
-- Table swap
-- -----------------------------------------------------
CREATE TABLE swap (
  id_pc_swap serial NOT NULL ,
  id_pc VARCHAR(45) NULL ,
  total VARCHAR(45) NULL ,
  used VARCHAR(45) NULL ,
  free VARCHAR(45) NULL ,
  timereg VARCHAR(45) NULL ,
  dayreg VARCHAR(45) NULL ,
  PRIMARY KEY (id_pc_swap) );

-- -----------------------------------------------------
-- Table discs
-- -----------------------------------------------------
CREATE TABLE discs (
  id_pc_discs serial NOT NULL ,
  id_pc VARCHAR(45) NULL ,
  s_fitxers VARCHAR(45) NULL ,
  size VARCHAR(45) NULL ,
  used_disc VARCHAR(45) NULL ,
  avail VARCHAR(45) NULL ,
  used VARCHAR(45) NULL ,
  mount VARCHAR(45) NULL ,
  timereg VARCHAR(45) NULL ,
  dayreg VARCHAR(45) NULL ,
  PRIMARY KEY (id_pc_discs) );



-- -----------------------------------------------------
-- Table usuaris
-- -----------------------------------------------------
CREATE TABLE usuaris (
  id_pc_usuari serial NOT NULL ,
  id_pc VARCHAR(45) NULL ,
  usuari VARCHAR(45) NULL ,
  timereg VARCHAR(45) NULL ,
  dayreg VARCHAR(45) NULL ,
  PRIMARY KEY (id_pc_usuari) );



-- -----------------------------------------------------
-- Table cpu
-- -----------------------------------------------------
CREATE TABLE cpu (
  id_pc_cpu serial NOT NULL ,
  id_pc VARCHAR(45) NULL ,
  valor1 VARCHAR(45) NULL ,
  valor2 VARCHAR(45) NULL ,
  timereg VARCHAR(45) NULL ,
  dayreg VARCHAR(45) NULL ,
  PRIMARY KEY (id_pc_cpu) );



-- -----------------------------------------------------
-- Table pcs
-- -----------------------------------------------------
CREATE TABLE pcs (
  id_pc_pcs serial NOT NULL ,
  id_pc VARCHAR(45) NULL ,
  estat VARCHAR(45) NULL ,
  timereg VARCHAR(45) NULL ,
  dayreg VARCHAR(45) NULL ,
  PRIMARY KEY (id_pc_pcs)
);
